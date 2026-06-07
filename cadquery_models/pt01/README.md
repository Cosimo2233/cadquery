# pt01 CadQuery Scripts

这些脚本是针对 `data-bin/pt01` 的手工 CadQuery 重建版本。

- `common.py`：通用齿形、极阵列、辐条等几何 helper
- `part_01.py` 到 `part_10.py`：每个零件各自的独立建模脚本
- `validate.py`：用 STL 作为参考，检查重建件的包围盒尺寸

所有脚本都使用 `mm` 作为单位，运行时不再读取 STL。

运行示例：

```python
from cadquery_models.pt01.part_03 import result
show_object(result)
```
