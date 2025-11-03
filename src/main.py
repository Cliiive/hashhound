from core.arg_parser import parse_arguments
from core.database import open_database, create_database_session, VicHashes
from core.logger import get_logger
from sqlalchemy import inspect
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
        session = create_database_session("test_files/hashes.db")
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        return 1
    
    results = session.query(VicHashes).all()
    
    if debug_mode:
        logger.debug(f"Retrieved {len(results)} records from VIC_HASHES table.")
        # Print the results
        for record in results:
            logger.debug(f"Record: {record.hash_value}")
    
    return 0
    

if __name__ == "__main__":
    main()