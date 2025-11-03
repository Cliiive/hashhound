from core.arg_parser import parse_arguments
from core.database import get_hashes
from core.logger import get_logger
from core.image_search import search_image_for_hashes
import sys

def print_params(evidence_path, hash_db_path, investigator_name, output_path, logger):
    logger.info("Parsed Command Line Arguments:")
    logger.info(f"Evidence Path   : {evidence_path}")
    logger.info(f"Hash DB Path    : {hash_db_path}")
    logger.info(f"Investigator    : {investigator_name}")
    logger.info(f"Output Path     : {output_path}")

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Access parsed arguments
    evidence_path = args.evidence
    hash_db_path = args.hash_db
    investigator_name = args.investigator
    output_path = args.output
    debug_mode = args.debug
    
    # Get singleton logger and set debug mode
    logger = get_logger()
    logger.set_debug_mode(debug_mode)
        
    # Print parsed arguments for verification
    print_params(evidence_path, hash_db_path, investigator_name, output_path, logger)
    
    try:
        hashes = get_hashes()
        logger.debug(f"Retrieved {len(hashes)} records from VIC_HASHES table.")
        for record in hashes:
            logger.debug(f"Hash : {record}")
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        return 1

    search_image_for_hashes(evidence_path, hashes)
        
    return 0
    

if __name__ == "__main__":
    main()