# YAML recipe file format
The recipe file follows the standard [YAML](https://en.wikipedia.org/wiki/YAML) format which gives an easy, human-readable method of representing an hierarchical structured document that can be easily parsed by software. The `bprc` recipe must follow the YAML format and must be appropriately indented. It has 2 top-level sections as illustrated below:
```yaml
---
variables:
  *<variables>*
recipe:
  *<recipe steps>*

```
