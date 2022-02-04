- CPU.run() -> 对应run
- CPU.run_single_cycle() ->对应single step
- CPU.get_all_reg() -> 获取所有返回结果
- CPU.memory.init_program(file_path) -> 从内存load程序
- CPU.[reg].set([value]) -> reg寄存器设置数值-> 用于LD
- CPU.store() -> store mbr，用于store
- CPU.load() -> load mbr, 用于load键


前端逻辑每次执行完毕后需要执行一次 `CPU.get_all_reg()` 来刷新所有寄存器数值，该函数return可以参考以下格式

```{'pc': '0000000000001101', 'mar': '0000000000001100', 'mbr': '0000011000001010', 'gpr0': '1011110011011110', 'gpr1': '1010101111001101', 'gpr2': '1011110011011110', 'gpr3': '0000000000000000', 'ixr1': '0000000000000000', 'ixr2': '0000000000000000', 'ixr3': '0000000000000000', 'cc': '0000000000000000', 'mfr': '0000000000000000', 'ir': '0000011000001010'}```