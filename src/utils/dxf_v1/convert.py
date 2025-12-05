import os
from pathlib import Path
import ezdxf  # <- make sure ezdxf is imported
import ezdxf.addons.odafc as odafc  # <- import the ODA converter

# Path to your AppImage
ODA_APPIMAGE = "/usr/local/bin/ODAFileConverter.real"
odafc.unix_exec_path = ODA_APPIMAGE
os.environ["QT_QPA_PLATFORM"] = "xcb"


def convert_dxf_to_dwg(
    dxf_path: str, output_dir: str = "/tmp", dwg_version="AC1024"
) -> str:
    dxf_path = Path(dxf_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dwg_file = output_dir / (dxf_path.stem + ".dwg")

    try:
        odafc.convert(
            source=str(dxf_path),
            dest=str(dwg_file),
            version=dwg_version,
            audit=True,
            replace=True,
        )
    except ezdxf.addons.odafc.UnknownODAFCError:
        # Ignore false errors on Linux
        pass

    if not dwg_file.exists():
        raise RuntimeError(f"Conversion failed: {dwg_file} was not created")

    return str(dwg_file)
