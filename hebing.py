# python
import shutil
from pathlib import Path

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}


def rename_images_in_folder(folder_path, prefix="", start_num=1, pad=4, merge_to=None):
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"错误: {folder_path} 不是有效文件夹")
        return start_num

    # 创建合并目标文件夹
    if merge_to:
        merge_path = Path(merge_to)
        merge_path.mkdir(parents=True, exist_ok=True)

    counter = start_num
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            new_name = f"{prefix}_{counter:0{pad}d}{p.suffix.lower()}" if prefix else f"{counter:0{pad}d}{p.suffix.lower()}"
            new_path = folder / new_name
            p.rename(new_path)
            print(f"{p.name} -> {new_name}")

            # 复制到合并文件夹
            if merge_to:
                shutil.copy2(new_path, merge_path / new_name)
                print(f"  已复制到: {merge_to}")

            counter += 1
    return counter


if __name__ == "__main__":
    # 按顺序处理多个文件夹
    folders = [
        r"F:\cattle\1",
        r"F:\cattle\2",
        r"F:\cattle\D01_20231101092012",
        r"F:\cattle\D01_20231101100518",
        r"F:\cattle\D01_20231101105016",
        r"F:\cattle\D01_20231101113638",
        r"F:\cattle\D01_20231101122302",
        r"F:\cattle\D01_20231101130928",
        r"F:\cattle\D01_20231101135552",
        r"F:\cattle\D01_20231101144220",
        r"F:\cattle\D01_20231101152847",
        r"F:\cattle\D01_20231101161515",
        r"F:\cattle\D01_20231101170141",
        r"F:\cattle\D01_20231101174805",
        r"F:\cattle\D02_20231002175456",
        r"F:\cattle\D02_20231101070615",
        r"F:\cattle\D02_20231101075243",
        r"F:\cattle\D02_20231101083911",
        r"F:\cattle\D02_20231101092535",
        r"F:\cattle\D02_20231101101203",
        r"F:\cattle\D02_20231101105831",
        r"F:\cattle\D02_20231101114459",
        r"F:\cattle\D02_20231101123127",
        r"F:\cattle\D02_20231101131755",
        r"F:\cattle\D02_20231101140422",
        r"F:\cattle\D02_20231101145048",
        r"F:\cattle\D02_20231101153716",
        r"F:\cattle\D02_20231101162344",
        r"F:\cattle\D02_20231101171012",
        r"F:\cattle\D03_20231001120354",
        r"F:\cattle\D03_20231006113832",
        r"F:\cattle\D03_20231101070427",
        r"F:\cattle\D03_20231101081604",
        r"F:\cattle\D03_20231101092720",
        r"F:\cattle\D03_20231101103810",
        r"F:\cattle\D03_20231101114913",
        r"F:\cattle\D03_20231101141031",
        r"F:\cattle\D03_20231101152042",
        r"F:\cattle\D03_20231101130021",
        r"F:\cattle\D03_20231101163046",
        r"F:\cattle\D04_20231030110833",
        r"F:\cattle\D06_20231006105938",
        r"F:\cattle\D06_20231030165136",
        r"F:\cattle\D07_20231030081326",
        r"F:\cattle\D08_20231030133811",
        r"F:\cattle\D09_20231030143328",
        r"F:\cattle\train",
    ]
    prefix = "images"
    counter = 1
    merge_target = r"F:\cattle\train"

    for folder in folders:
        print(f"\n处理文件夹: {folder}")
        counter = rename_images_in_folder(folder, prefix=prefix, start_num=counter, pad=4, merge_to=merge_target)
