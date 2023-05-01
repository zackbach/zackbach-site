+++
title = '{{ replace .Name "-" " " | title }}'
date = {{ .Date }}
tags = []
thumbnail = '{{ path.Join .Name ".*" }}'
summary = 'PLACEHOLDER'
+++