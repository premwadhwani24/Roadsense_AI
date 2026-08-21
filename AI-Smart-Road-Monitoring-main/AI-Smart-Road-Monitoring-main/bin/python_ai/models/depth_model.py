def calculate_geometry(payload: dict):
    depth = payload.get("depth", 1.5)
    width = payload.get("width", 2.0)

    volume = depth * width * 0.5

    return {
        "depth": depth,
        "width": width,
        "volume_estimate": volume
    }
