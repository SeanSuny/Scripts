#!/bin/bash
## 导出本地所有账号

## 格式一
echo -e "\nexport JD_COOKIE=\"${JD_COOKIE}\"\n"
## 格式二
echo "${JD_COOKIE}" | perl -pe '{s|&|\n|g}' | perl -pe '{s|^|\"|g, s|;$|;\",|g}'

echo -e ''
