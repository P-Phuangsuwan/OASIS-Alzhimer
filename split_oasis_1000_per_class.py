from pathlib import Path
import random
import shutil


# จำนวนรูปที่ต้องการคัดลอกจากแต่ละคลาส
IMAGES_PER_CLASS = 1000

# ค่า seed ทำให้การสุ่มได้ผลเหมือนเดิมทุกครั้งที่รัน
# ถ้าต้องการสุ่มชุดใหม่ ให้เปลี่ยนเลขนี้เป็นค่าอื่น
RANDOM_SEED = 42

# ถ้าเป็น True สคริปต์จะค้นหารูปในโฟลเดอร์ย่อยด้วย
SEARCH_SUBFOLDERS = True

# ถ้าคลาสใดมีรูปน้อยกว่า 1000:
# - True  = สุ่มรูปซ้ำบางไฟล์เพื่อให้ครบ 1000 รูป
# - False = หยุดทำงานและแจ้ง error
ALLOW_DUPLICATES_IF_NOT_ENOUGH = True

# โฟลเดอร์ต้นทางของแต่ละคลาส
SOURCE_DIRS = {
    "Moderate Dementia": Path(r"D:\OASIS Alzheimer\Data\Moderate Dementia"),
    "Non Demented": Path(r"D:\OASIS Alzheimer\Data\Non Demented"),
    "Very mild Dementia": Path(r"D:\OASIS Alzheimer\Data\Very mild Dementia"),
    "Mild Dementia": Path(r"D:\OASIS Alzheimer\Data\Mild Dementia"),
}

# โฟลเดอร์ปลายทาง สคริปต์จะสร้างโฟลเดอร์ย่อยแยกตามชื่อคลาสให้อัตโนมัติ
OUTPUT_DIR = Path(r"D:\OASIS Alzheimer\Data_1000_each")

# นามสกุลไฟล์ภาพที่ยอมรับ
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def find_images(folder: Path) -> list[Path]:
    """ค้นหาไฟล์รูปภาพทั้งหมดในโฟลเดอร์"""
    search_pattern = "**/*" if SEARCH_SUBFOLDERS else "*"
    return sorted(
        file_path
        for file_path in folder.glob(search_pattern)
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS
    )


def copy_images(class_name: str, source_dir: Path, output_dir: Path) -> None:
    """สุ่มรูปจากคลาสเดียว แล้วคัดลอกไปยังโฟลเดอร์ปลายทางของคลาสนั้น"""
    images = find_images(source_dir)

    if not images:
        raise ValueError(f"คลาส '{class_name}' ไม่มีไฟล์ภาพที่อ่านได้")

    if len(images) < IMAGES_PER_CLASS and not ALLOW_DUPLICATES_IF_NOT_ENOUGH:
        raise ValueError(
            f"คลาส '{class_name}' มีรูปแค่ {len(images)} รูป "
            f"แต่ต้องการ {IMAGES_PER_CLASS} รูป"
        )

    if len(images) >= IMAGES_PER_CLASS:
        # ถ้ามีรูปเพียงพอ จะสุ่มแบบไม่ซ้ำ
        selected_images = random.sample(images, IMAGES_PER_CLASS)
    else:
        # ถ้ามีรูปไม่พอ จะใช้ทั้งหมดก่อน แล้วสุ่มซ้ำจากชุดเดิมจนกว่าจะครบ
        selected_images = images + random.choices(images, k=IMAGES_PER_CLASS - len(images))
        random.shuffle(selected_images)
        print(
            f"คำเตือน: คลาส '{class_name}' มีรูปจริง {len(images)} รูป "
            f"จึงมีบางไฟล์ถูกสุ่มซ้ำเพื่อให้ครบ {IMAGES_PER_CLASS} รูป"
        )

    class_output_dir = output_dir / class_name
    class_output_dir.mkdir(parents=True, exist_ok=True)

    for index, image_path in enumerate(selected_images, start=1):
        # เติมเลขลำดับหน้าไฟล์เพื่อป้องกันชื่อไฟล์ซ้ำ และยังเก็บชื่อเดิมไว้ด้านหลัง
        new_name = f"{index:04d}_{image_path.name}"
        shutil.copy2(image_path, class_output_dir / new_name)

    print(f"คัดลอก {len(selected_images)} รูป: {class_name} -> {class_output_dir}")


def main() -> None:
    """จุดเริ่มต้นของโปรแกรม"""
    random.seed(RANDOM_SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for class_name, source_dir in SOURCE_DIRS.items():
        if not source_dir.exists():
            raise FileNotFoundError(f"ไม่พบโฟลเดอร์ต้นทาง: {source_dir}")

        copy_images(class_name, source_dir, OUTPUT_DIR)

    print(f"\nเสร็จแล้ว ไฟล์ทั้งหมดถูกบันทึกไว้ที่: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
