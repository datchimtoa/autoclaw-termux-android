# peel.py
# Chạy: python peel.py thtool.py

import builtins, sys, pathlib, hashlib

real_compile = builtins.compile
real_exec = builtins.exec

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
out = pathlib.Path("recovered")
out.mkdir(exist_ok=True)

seen = set()
stage_no = 0

def decode_once(text):
    global stage_no
    captured = []

    def safe_compile(source, *args, **kwargs):
        code = source.decode("utf-8", "replace") if isinstance(source, (bytes, bytearray)) else source
        captured.append(code)
        raise SystemExit

    builtins.compile = safe_compile
    builtins.exec = lambda *a, **k: (_ for _ in ()).throw(SystemExit)
    try:
        real_exec(real_compile(text, "layer.py", "exec"))
    except SystemExit:
        pass
    finally:
        builtins.compile = real_compile
        builtins.exec = real_exec

    return captured

for layer in range(20):
    results = decode_once(src)
    new = []
    for code in results:
        h = hashlib.sha256(code.encode("utf-8", "replace")).hexdigest()
        if h not in seen:
            seen.add(h)
            stage_no += 1
            path = out / f"layer{layer}_stage{stage_no}.py"
            path.write_text(code, encoding="utf-8")
            print(f"[+] layer {layer} -> {path} ({len(code)} chars)")
            new.append(code)

    if not new:
        print("[!] Không còn lớp mã hóa mới.")
        break

    # chọn payload lớn nhất mới nhất để bóc tiếp
    src = max(new, key=len)

print("[✓] Xong. Kiểm tra thư mục recovered/")
