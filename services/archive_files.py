import datetime
import hashlib
import json
import logging
import os
import shutil


logging.basicConfig(level=logging.INFO)

archive_dir = os.getenv("ARCHIVE_DIRECTORY")
logging.info("The archive directory is %s", archive_dir)
log_file = os.path.join(archive_dir, "audit.log")
os.makedirs(archive_dir, exist_ok=True)


def _compute_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def _save_metadata(unique_name: str, metadata: dict):
    meta_path = os.path.join(archive_dir, f"{unique_name}.meta.json")
    with open(meta_path, "w") as file:
        json.dump(metadata, file, indent=2)


def _log_action(action: str, metadata: dict):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action,
        "details": metadata
    }
    with open(log_file, "a") as file:
        file.write(json.dumps(log_entry) + "\n")


async def archive_file(
        file_path: str,
        file_type: str,
        sender: str,
        receiver: str,
        original_filename: str
) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.info("Archiving file at %s", timestamp)
    unique_name = f"{timestamp}_{sender}_{receiver}_{file_type}_{original_filename}"
    logging.info("The unique name for the archived file is %s", unique_name)
    archive_path = os.path.join(archive_dir, unique_name)
    logging.info("The archive path is %s", archive_path)
    shutil.copy2(file_path, archive_path)
    logging.info("File copied to archive directory")

    file_hash = _compute_hash(archive_path)
    metadata = {
        "archived_at": timestamp,
        "sender": sender,
        "receiver": receiver,
        "file_type": file_type,
        "original_filename": original_filename,
        "archive_path": archive_path,
        "hash": file_hash
    }
    _save_metadata(unique_name, metadata)
    _log_action("ARCHIVE", metadata)
    return archive_path
