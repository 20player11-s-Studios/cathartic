def human_size(size: int) -> str:
    s = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(s) < 1024:
            return f"{s:.1f} {unit}"
        s /= 1024
    return f"{s:.1f} PB"
