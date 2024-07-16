Historically, there was much debate over how structs are passed (directly or indirectly), which ties into the multivalue proposal. The star of the show is (perhaps unsurprisingly, given the state of general ABI discourse) the C ABI for Wasm. In chronological order...

`wasm-unknown-unknown` was added as a compilation target, and `wasm-bindgen` was written (with some naive encoding). However, `wasm-bindgen` did not match the [C ABI for Wasm](https://github.com/WebAssembly/tool-conventions/blob/main/BasicCABI.md) used by Clang/LLVM
- Ex: Clang and Rustc [vary](https://github.com/WebAssembly/tool-conventions/issues/130) in how structs arguments are passed. Clang passes a pointer, while Rust passes a handful of parameters (which `wasm-bindgen` expects)
    - See also this [old discussion](https://github.com/WebAssembly/tool-conventions/issues/88) (on the C ABI repo!), which is likely more comprehensive
- Much of this discussion centers around Wasm's multi-value returns, which the standard C ABI for Wasm does not use

A `wasm` ABI was [added](https://github.com/rust-lang/rust/pull/83763) (see [tracking issue](https://github.com/rust-lang/rust/issues/83788)) with splatting and multi-value support (for use by `wasm-bindgen`), with the intention of having the the default `wasm-unknown-unknown` ABI changed to match the C ABI for Wasm
- The idea is that you could use `extern "wasm"` to get this, and `extern "C"` otherwise. Using `wasm-bindgen` would require this `extern "wasm"`, after the breaking change is made
    - Currently, the `wasm-bindgen` macro will generate a new version of the function which is marked as `extern "C"` (while also wrapping things up, etc)
- The goal here is to match the Wasm standard, not how Clang does things—more direct translation, matching signatures more precisely, etc
- Much of the [discussion](https://github.com/rust-lang/rust/issues/83788#issuecomment-1191564068) here is that the C ABI for Wasm may change to support multi-value returns in an unknown way (they still do not have support for it, AFAICT), thus they want to separate out the two treatments

There has been debate over what `extern "wasm"` actually does or should do
- The [core of the issue](https://github.com/rust-lang/rust/issues/83788#issuecomment-1562649508) is that `extern "wasm"` is a by-product of LLVM codegen: there are a [lack of guarantees](https://github.com/rust-lang/rust/issues/83788#issuecomment-1562684547) on how LLVM / rustc do things!!
    - There are even [other issues](https://github.com/rust-lang/rust/issues/115666) (plus [tracking](https://github.com/rust-lang/rust/issues/119183)) [describing](https://github.com/rust-lang/rust/issues/83788#issuecomment-1710277392) how passing aggregate types directly makes it hard to reason about ABI compatibility, since things depend on how LLVM specifically lowers these struct types
- [This comment](https://github.com/rust-lang/rust/issues/83788#issuecomment-1562812884) gives a good overview on the differences between `extern "wasm"` and `extern "C"` ABI differences, which links to the comprehensive [`extern "wasm"` meeting notes](https://github.com/rust-lang/lang-team/blob/master/design-meeting-minutes/2021-04-21-wasm-abi.md)

At this point in history, `extern "C"` on [all](https://github.com/rust-lang/rust/issues/83788#issuecomment-1562799411) targets implemented the C ABI for Wasm, except `wasm-unknown-unknown` which was holding out due to `wasm-bindgen`. `wasm-bindgen` had [plans to change](https://github.com/rustwasm/wasm-bindgen/issues/3454) (the issue has a great summary), and eventually [`wasm-bindgen` was updated](https://github.com/rustwasm/wasm-bindgen/pull/3595)! This allowed the `extern "C"` code to be compiled in a way that is compliant with the C ABI for Wasm
- To ease the transition period, the `-Z wasm-c-abi` flag was [added](https://github.com/rust-lang/rust/pull/117919) to allow users to compile to `wasm-unknown-unknown` with the new, compliant behavior
- This flag will eventually be [obsolete](https://github.com/rust-lang/rust/pull/117918), once the compliant behavior is the default

Recently, LLVM has [changed](https://github.com/llvm/llvm-project/pull/88492) how it supports multivalue returns. LLVM backend support for the feature [works in theory](https://github.com/rust-lang/rust/issues/127318#issuecomment-2214257179) but is still [buggy](https://github.com/llvm/llvm-project/issues/98323)
- Updating LLVM [triggered a discussion](https://github.com/rust-lang/rust/pull/127513), which relates to [pre-existing concerns](https://github.com/rustwasm/wasm-bindgen/issues/3454#issuecomment-2189386518)
- It [appears](https://github.com/rust-lang/rust/pull/127513#issuecomment-2220506527) that multivalue support is now enabled by default, but only for the `experimental-mv` ABI, instead of being per-function tweaks
- This means that the `extern "wasm"` ABI, which was like the (pre-C compliant) ABI with per-function multivalue support, is not really applicable, and [considered a failed experiment](https://github.com/rust-lang/rust/pull/127513#issuecomment-2220650081)
- I believe that they do not want to use the `experimental-mv` flag (since they want to be compliant with the C ABI for Wasm), and that multivalue won't exist until Clang makes a decision and changes the C ABI for Rust
    - Alex [says](https://github.com/rust-lang/rust/pull/127513#issuecomment-2220650081) "multivalue just isn't feasible with LLVM", and all related tests are currently disabled

This brings us to the [current state](https://github.com/rust-lang/rust/pull/127513#issuecomment-2220742869) of the Wasm ABI: compiling with `-Z wasm-c-abi=spec` will use the C ABI for Wasm (which will eventually be the default), and compiling with `-Z wasm-c-abi=legacy` will use the default, pre-compliant ABI
- The `extern "wasm"` ABI has [been removed](https://github.com/rust-lang/rust/pull/127605)
- It feels like [Alex's comment](https://github.com/rust-lang/rust/issues/83788#issuecomment-1563118074) has come true, where we are left waiting on upstream (Clang) to change how C is compiled to Wasm using the multivalue
    - These changes to the C ABI for Wasm would likely be based on performance concerns, not expressivity
    - [Specifically](https://github.com/rust-lang/rust/pull/127513#issuecomment-2223061784), multivalue is on by default but does not do anything unless the `experimental-mv` is used; we are waiting on good multivalue support in LLVM
- [Some think](https://github.com/WebAssembly/tool-conventions/pull/161#issuecomment-759844146) the multivalue ABI will be a different C ABI for Wasm, with the current ABI being kept for legacy reasons
- [Apparently](https://github.com/llvm/llvm-project/pull/88492#issue-2239616346), WASI is planning to add a multivalue ABI soon
- Code example of interop: check out [this example repo](https://github.com/rafaelbeckel/test-c-rust-wasm)


`wasm-unknown-unknown` is also not the only target! Specifically, `wasm-wasi` exists as well, which supports WASI. In `wasm-unknown-unknown`, much of `std` (ex: opening files, etc) will just fail, while in `wasm-wasi`, this will actually work (using the `wasi` API)
- This mainly makes a difference when it comes to targets, according to [this meeting](https://youtu.be/XH4sXBa06ig?t=1206). Specifically, WASI is usually used for non-web targets, while `unknown-unknown` came first and is used for the web
- As of [recently](https://blog.rust-lang.org/2024/04/09/updates-to-rusts-wasi-targets.html), `wasm-wasi` was renamed `wasm-wasip1` (for preview 1 AKA WASI 0.1), and `wasm-wasip2` was added as a target as well
- `wasm-wasi` is [intended](https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html) to be able to work with any other language compiled to Wasm (like C), and ABI differences are considered bugs
    - Working with C and being hassle-free [are at-odds](https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1-threads.html)


There is another related project, [Emscripten](https://github.com/emscripten-core/emscripten), which compiles C(++) to Wasm using Clang and LLVM
- Apparently, any other language that uses LLVM can use Emscripten as well
    - This includes Rust: `wasm-unknown-emscripten` integrates Emscripten with Rust (even though it apparently[ has some issues](https://github.com/rust-lang/rust/issues/66916))
    - From [Reddit](https://www.reddit.com/r/rust/comments/17oaz2x/comment/k7xztgp/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button), this target is currently "your mileage may vary"
- Emscripten uses Clang for some heavy lifting; Clang can compile Wasm as well, but Emscripten has [better](https://stackoverflow.com/questions/64690937/what-is-the-difference-between-emscripten-and-clang-in-terms-of-webassembly-comp) integration with JavaScript, POSIX interfaces, etc
    - It appears that it is designed to compile C code that is less limited
    - WASI seems to be working into this niche, a little bit
    - [This article](https://hacks.mozilla.org/2019/03/standardizing-wasi-a-webassembly-system-interface/) proposing WASI explains that Emscripten emulates POSIX interface: the programmer can use `libc`, which is partially compiled into Wasm, and partially implemented using JS glue code
        - This 
- This [PR](https://github.com/rust-lang/rust/pull/63649) seems to have a lot of relevant discussion, though it's fairly old (but mentioned again [here](https://github.com/WebAssembly/tool-conventions/issues/88#issuecomment-543885030))



## Connections with LLVM

In reality, the Rust code is being compiled to LLVM IR, from which Wasm is generated. This means that things can change depending on the LLVM types that are used, along with how LLVM actually lowers these during code generation (mentioned [here](https://github.com/rust-lang/rust/issues/83788#issuecomment-1477045004))
- It's interesting to think about what a stable world looks like here, given the reality that Rust is compiled to LLVM IR, and codegen is separate (by LLVM)
    - Would we need a separate direct-to-Wasm compiler? Would we just restrict the types of optimizations that LLVM can make (which could impact other compilation?)
- This also feels like it ties to some ideas about compositionality and multi-pass compilers that Andrew and I discussed a few weeks ago
- From a [previous discussion](https://github.com/rust-lang/rust/issues/83788#issuecomment-1562649508), "`extern "wasm"` implements some weird ABI that is decided by the interaction between LLVM (maybe stable?) and the exact way rustc_codegen_llvm uses struct types in arguments (definitively not stable!)."
- Swift is [able to](https://github.com/swiftlang/swift/blob/main/docs/ABI/TypeLayout.rst) "get the necessary control over the binary layout" by adding manual padding to struct types, for instance
- This [comment](https://github.com/WebAssembly/tool-conventions/issues/54#issuecomment-824274703) from Alex gives insight into his idea for an alternative LLVM-level ABI

It feels like the main thing that is tying Rust down to how Clang implements things is wanting to be compliant with the C ABI for Wasm (which is sorta just Clang's thing)
- Alex has [claimed](https://github.com/WebAssembly/tool-conventions/issues/88#issuecomment-544575709) that the C ABI for Wasm is "whatever Clang happened to implement". Others have [disagreed](https://github.com/WebAssembly/tool-conventions/issues/88#issuecomment-544601994) noting the decisions made were conscious
    - Regardless of how it came to be, the reality of the situation is that we are still waiting for Clang to make changes, and can't proceed because of that
- If Rust broke away from this C ABI, presumably the LLVM that gets generated would be treated similarly to that of Swift, following the [Swift ABI for Wasm](https://github.com/WebAssembly/tool-conventions/blob/main/SwiftABI.md)
    - I would assume that any LLVM IR optimizations that break ABI compliance (for Swift currently, perhaps for Rust later) would simply be considered bugs
    - I don't know how LLVM optimizes things, or how the Swift ABI is implemented with respect to LLVM either
- [This post](https://discourse.llvm.org/t/questions-about-c-calling-conventions/72414) discusses how it is almost necessary to [reimplement code](https://discourse.llvm.org/t/questions-about-c-calling-conventions/72414/2) for different calling conventions, since more information is needed than is available in LLVM types
    - [Some things](https://discourse.llvm.org/t/questions-about-c-calling-conventions/72414/9) like pointers, registered-sized integers, etc _should be lowered "as C ABI"_ on all LLVM targets. This appears to be as guaranteed as anything is by LLVM

## General Ideas

Sentiments, from the Rust team:
- It is hard to stabilize a Wasm ABI, since Wasm is always evolving
    - Ex: What if we said that a `u132` is represented as two `u64`, but now Wasm adds `u132` support in a later version?
- TODO: more here

Sentiments, from Zack:
- The current state of things relies on LLVM and Clang, a _lot_
    - The Swift compiler literally uses Clang, other things will target LLVM and inherit a lot from it
    - Things oftentimes have to be updated [simultaneously](https://github.com/WebAssembly/wasi-libc/pull/152#issuecomment-592177864) in multiple places, like in the [documentation](https://github.com/WebAssembly/tool-conventions/pull/134), [Clang](https://reviews.llvm.org/D70700), and [wasi-libc](https://github.com/WebAssembly/wasi-libc/pull/152)

Project Ideas:
- I think a lot of our ideas about this project will come with how closely we want to stay tied to the C ABI for Wasm
    - If we are straying away already (instead of building on top of), then it feels like there's no reason not to do multi-value returns and splat things, which is just faster
    - It feels like most current proposals are tied to the C ABI for Wasm, though
    - While Swift-style ABI flexibility seems nice, it is very anti-Rust
- The main calling convention questions seem to be related to multiple returns and indirect returns (through a pointer, vs by value)
- There are probably interesting implications for [field order](https://youtu.be/XH4sXBa06ig?t=1707) when it comes to splatting vs passing a pointer
    - This could be cool to explore along with the `non_exhaustive` attribute
- We should think about [unsized types](https://doc.rust-lang.org/book/ch19-04-advanced-types.html), maybe look at [trait objects](https://articles.bchlr.de/traits-dynamic-dispatch-upcasting) (see [object safety](https://huonw.github.io/blog/2015/01/object-safety/)?)
- We'll probably have to think about name mangling, and imports/exports somehow
- There is no String type, obviously, which is important (especially considering the different Rust strings...)

Questions:
- Would `crABI` (which presumably would impact the LLVM IR that gets generated) implicitly define a WebAssembly ABI, given codegen?
    - Could something like this be formalized? Like $e^{+} \in \mathcal{LABI}[[\tau]] \triangleq e \in \mathcal{UABI}[[\tau]]$ (or perhaps just that there exists a backtranslation in the upper-level ABI)
    - Morally, this probably isn't something you want: you shouldn't entirely base an ABI off of a single compiler implementation, even if that is sorta happening in practice
- You can take an ABI (indexed by source types and inhabited by IR terms) and add in a compiler to get a new ABI inhabited by target terms
    - This feels sorta like what has happened for C and Swift (with an implicit ABI at the level of LLVM IR, extended to Wasm through LLVM's code generation), and what could possibly happen with Rust plus crABI
    - What if we had a Rust ABI inhabited by RichWasm terms, then we extend to a normal Wasm ABI with this backtranslation-like method? Does this give us anything useful? Is this too reliant on the existing compiler? How could this support evolution? Is there a natural notion of how this code generating compiler can evolve while maintaining compatibility?


# Rust ABI
(not WebAssembly specific)

[This post](https://users.rust-lang.org/t/question-about-abi-in-wasm/85599/2) explains that types (like `Option`, `String`, etc) without a `#[repr(...)]` attribute have no ABI stability guarantees, and suggests defining wrapper types with a stable layout
- The post does note that option of some things (like `Option<NonNull<T>>`) _is_ stable