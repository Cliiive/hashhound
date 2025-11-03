import pytsk3
from .logger import get_logger

def search_image_for_hash(image_path, target_hash):
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
                if partition.len > 2048:  # Skip small partitions
                    logger.info(f"Searching partition at offset {partition.start}")
                    try:
                        # Create filesystem for this partition
                        fs = pytsk3.FS_Info(img, offset=partition.start * volume.info.block_size)
                        search_filesystem(fs, target_hash)
                    except Exception as e:
                        logger.error(f"Could not access filesystem on partition at offset {partition.start}: {e}")
        except:
            # No partition table found, try as single filesystem
            logger.info("No partition table found, treating as single filesystem")
            fs = pytsk3.FS_Info(img)
            search_filesystem(fs, target_hash)
            
    except Exception as e:
        logger.error(f"Error opening image {image_path}: {e}")

def search_filesystem(fs, target_hash):
    """Search a single filesystem for the target hash."""
    logger = get_logger()
    
    # Walk through the filesystem
    for dirpath, dirnames, filenames in fs.walk('/'):
        for filename in filenames:
            file_path = f"{dirpath}/{filename}"
            try:
                file_obj = fs.open(file_path)
                file_data = file_obj.read_random(0, file_obj.info.meta.size)
                
                # Compute hash (assuming SHA256 for this example)
                import hashlib
                file_hash = hashlib.sha256(file_data).hexdigest()
                
                if file_hash == target_hash:
                    logger.info(f"Found matching file: {file_path}")
            
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")