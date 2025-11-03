import pytsk3
from pathlib import Path
import time
from core.logger import get_logger

def search_image_for_hashes(image_path, hashes):
    """
    Search a disk image for a specific hash value.
    
    Args:
        image_path (str): Path to the disk image file.
        target_hash (str): The hash value to search for.
    """
    logger = get_logger()
    
    try:
        # Open the disk image
        img = pytsk3.Img_Info(image_path)
        
        # Try to get volume/partition information
        try:
            volume = pytsk3.Volume_Info(img)
            # Iterate through partitions
            for partition in volume:
               
                logger.info(f"Searching partition at offset {partition.start}")
                try:
                    # Create filesystem for this partition
                    fs = pytsk3.FS_Info(img, offset=partition.start * volume.info.block_size)
                    search_filesystem(fs, hashes)
                except Exception as e:
                    logger.error(f"Could not access filesystem on partition at offset {partition.start}: {e}")
        except:
            # No partition table found, try as single filesystem
            logger.info("No partition table found, treating as single filesystem")
            fs = pytsk3.FS_Info(img)
            search_filesystem(fs, hashes)
            
    except Exception as e:
        logger.error(f"Error opening image {image_path}: {e}")

def walk_fs(fs, path="/"):
    try:
        directory = fs.open_dir(path)
    except IOError:
        return
    for entry in directory:
        if not hasattr(entry, "info") or not entry.info.name:
            continue
        name = entry.info.name.name.decode(errors="ignore")
        if name in [".", ".."] or name.startswith("$"):
            continue
        full_path = "/".join([path.strip("/"), name]).replace("//", "/")
        if entry.info.meta and entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
            yield from walk_fs(fs, "/" + full_path)
        else:
            yield "/" + full_path

def search_filesystem(fs, hashes):
    logger = get_logger()
    
    processed_files = 0
    matches_found = 0
    last_progress_time = time.time()
    progress_interval = 1.0  # Report progress every 5 seconds
    start_time = time.time()
    
    logger.info("Starting filesystem search...")
    
    for file_path in walk_fs(fs):
        try:
            logger.debug(f"Processing file: {file_path}")
            file_obj = fs.open(file_path)
            size = file_obj.info.meta.size
            data = file_obj.read_random(0, size) if size else b""
            import hashlib
            file_hash = hashlib.sha256(data).hexdigest()
            if file_hash in hashes:
                matches_found += 1
                logger.info(f"Found matching file for hash << {file_hash[0:5]}...{file_hash[-6:-1]} >> at {file_path}")
        except Exception as e:
            logger.warning(f"Error processing file {file_path}: {e}")
        
        processed_files += 1
        
        # Report progress periodically with rate information
        current_time = time.time()
        if current_time - last_progress_time >= progress_interval:
            elapsed_time = current_time - start_time
            files_per_second = processed_files / elapsed_time
            logger.info(f"Search progress: {processed_files} files processed, {matches_found} matches found ({files_per_second:.1f} files/sec)")
            last_progress_time = current_time