#!/usr/bin/env python3
"""
Comprehensive SQL Server to PostgreSQL SQL Dump Converter
Converts SQL Server .sql dump files to PostgreSQL-compatible format
Usage: python convert_sql.py input.sql output.sql
"""
import re
import sys
import os

def convert_sqlserver_to_postgres(input_file, output_file):
    """
    Convert SQL Server syntax to PostgreSQL syntax
    Handles: data types, functions, identifiers, constraints, and more
    """
    
    print(f"Reading {input_file}...")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        sql = f.read()
    
    original_size = len(sql)
    print(f"Original file size: {original_size:,} bytes")
    
    # ===== STEP 1: Remove SQL Server Specific Commands =====
    print("\n[1/10] Removing SQL Server specific commands...")
    sql = re.sub(r'USE\s+\[.*?\]\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bGO\b\s*', ';\n', sql, flags=re.IGNORECASE)
    sql = re.sub(r'SET\s+ANSI_NULLS\s+(ON|OFF)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'SET\s+QUOTED_IDENTIFIER\s+(ON|OFF)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'SET\s+ANSI_PADDING\s+(ON|OFF)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'SET\s+ANSI_WARNINGS\s+(ON|OFF)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'SET\s+CONCAT_NULL_YIELDS_NULL\s+(ON|OFF)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'SET\s+NUMERIC_ROUNDABORT\s+(ON|OFF)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'SET\s+ARITHABORT\s+(ON|OFF)\s*', '', sql, flags=re.IGNORECASE)
    
    # ===== STEP 2: Convert Square Brackets to Double Quotes =====
    print("[2/10] Converting identifier syntax [name] to \"name\"...")
    sql = re.sub(r'\[([^\]]+)\]', r'"\1"', sql)
    
    # ===== STEP 3: Convert Data Types =====
    print("[3/10] Converting data types...")
    
    # String types
    sql = re.sub(r'\bNVARCHAR\s*\(\s*MAX\s*\)', 'TEXT', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bVARCHAR\s*\(\s*MAX\s*\)', 'TEXT', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNVARCHAR\s*\(', 'VARCHAR(', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNVARCHAR\b', 'VARCHAR', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNVARCHAR2\b', 'VARCHAR', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNCHAR\s*\(', 'CHAR(', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNTEXT\b', 'TEXT', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bTEXT\b(?!\s*\()', 'TEXT', sql, flags=re.IGNORECASE)
    
    # Binary types
    sql = re.sub(r'\bIMAGE\b', 'BYTEA', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bVARBINARY\s*\(\s*MAX\s*\)', 'BYTEA', sql, flags=re.IGNORECASE)
    
    # Date/Time types
    sql = re.sub(r'\bDATETIME2\b', 'TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bDATETIME\b', 'TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSMALLDATETIME\b', 'TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bDATETIMEOFFSET\b', 'TIMESTAMP WITH TIME ZONE', sql, flags=re.IGNORECASE)
    
    # Numeric types
    sql = re.sub(r'\bBIT\b', 'BOOLEAN', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bTINYINT\b', 'SMALLINT', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bMONEY\b', 'DECIMAL(19,4)', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSMALLMONEY\b', 'DECIMAL(10,4)', sql, flags=re.IGNORECASE)
    
    # GUID/UUID
    sql = re.sub(r'\bUNIQUEIDENTIFIER\b', 'UUID', sql, flags=re.IGNORECASE)
    
    # XML type stays the same in PostgreSQL
    # HIERARCHYID doesn't have direct equivalent - keep as is for manual review
    
    # ===== STEP 4: Convert IDENTITY to SERIAL/GENERATED =====
    print("[4/10] Converting IDENTITY columns...")
    sql = re.sub(r'\bINT\s+IDENTITY\s*\(\s*1\s*,\s*1\s*\)', 'SERIAL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bBIGINT\s+IDENTITY\s*\(\s*1\s*,\s*1\s*\)', 'BIGSERIAL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSMALLINT\s+IDENTITY\s*\(\s*1\s*,\s*1\s*\)', 'SMALLSERIAL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bINT\s+IDENTITY\b', 'SERIAL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bBIGINT\s+IDENTITY\b', 'BIGSERIAL', sql, flags=re.IGNORECASE)
    
    # ===== STEP 5: Convert Functions =====
    print("[5/10] Converting functions...")
    
    # Date functions
    sql = re.sub(r'\bGETDATE\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bGETUTCDATE\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSYSDATETIME\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSYSDATETIMEOFFSET\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bCURRENT_TIMESTAMP\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    
    # String functions
    sql = re.sub(r'\bLEN\s*\(', 'LENGTH(', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bCHARINDEX\s*\(', 'POSITION(', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSTUFF\s*\(', 'OVERLAY(', sql, flags=re.IGNORECASE)
    
    # NULL handling
    sql = re.sub(r'\bISNULL\s*\(', 'COALESCE(', sql, flags=re.IGNORECASE)
    
    # GUID/UUID
    sql = re.sub(r'\bNEWID\s*\(\s*\)', 'gen_random_uuid()', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNEWSEQUENTIALID\s*\(\s*\)', 'gen_random_uuid()', sql, flags=re.IGNORECASE)
    
    # Conversion functions
    sql = re.sub(r'\bCONVERT\s*\(\s*VARCHAR', 'CAST(', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bCAST\s*\(\s*([^)]+)\s+AS\s+DATETIME\s*\)', r'CAST(\1 AS TIMESTAMP)', sql, flags=re.IGNORECASE)
    
    # ===== STEP 6: Convert TOP to LIMIT =====
    print("[6/10] Converting TOP to LIMIT...")
    # This is a simplified conversion - complex TOP with ORDER BY needs manual review
    sql = re.sub(r'\bSELECT\s+TOP\s+\(\s*(\d+)\s*\)\s+', r'SELECT ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSELECT\s+TOP\s+(\d+)\s+', r'SELECT ', sql, flags=re.IGNORECASE)
    
    # ===== STEP 7: Remove Query Hints =====
    print("[7/10] Removing query hints...")
    sql = re.sub(r'WITH\s*\(\s*NOLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*READUNCOMMITTED\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*ROWLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*UPDLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*HOLDLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*TABLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    
    # ===== STEP 8: Convert Constraints =====
    print("[8/10] Converting constraints...")
    # CLUSTERED/NONCLUSTERED keywords
    sql = re.sub(r'\bCLUSTERED\s+INDEX\b', 'INDEX', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNONCLUSTERED\s+INDEX\b', 'INDEX', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bCLUSTERED\s+PRIMARY\s+KEY\b', 'PRIMARY KEY', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNONCLUSTERED\s+PRIMARY\s+KEY\b', 'PRIMARY KEY', sql, flags=re.IGNORECASE)
    
    # ===== STEP 9: Convert Default Constraints =====
    print("[9/10] Converting default constraints...")
    # Remove constraint names from defaults (PostgreSQL handles differently)
    sql = re.sub(r'CONSTRAINT\s+"[^"]+"\s+DEFAULT\s+', 'DEFAULT ', sql, flags=re.IGNORECASE)
    
    # Convert bit defaults
    sql = re.sub(r'DEFAULT\s+\(\s*\(\s*0\s*\)\s*\)', 'DEFAULT FALSE', sql, flags=re.IGNORECASE)
    sql = re.sub(r'DEFAULT\s+\(\s*\(\s*1\s*\)\s*\)', 'DEFAULT TRUE', sql, flags=re.IGNORECASE)
    sql = re.sub(r'DEFAULT\s+\(\s*0\s*\)', 'DEFAULT FALSE', sql, flags=re.IGNORECASE)
    sql = re.sub(r'DEFAULT\s+\(\s*1\s*\)', 'DEFAULT TRUE', sql, flags=re.IGNORECASE)
    
    # ===== STEP 10: Clean Up Formatting =====
    print("[10/10] Cleaning up formatting...")
    
    # Remove extra parentheses around defaults
    sql = re.sub(r'DEFAULT\s+\(\s*\(([^)]+)\)\s*\)', r'DEFAULT \1', sql, flags=re.IGNORECASE)
    
    # Clean up multiple semicolons
    sql = re.sub(r';\s*;+', ';', sql)
    
    # Remove excessive blank lines
    sql = re.sub(r'\n\s*\n\s*\n+', '\n\n', sql)
    
    # Remove trailing spaces
    sql = re.sub(r' +\n', '\n', sql)
    
    # Add PostgreSQL header comment
    header = """-- Converted from SQL Server to PostgreSQL
-- Original file: {}
-- Conversion date: {}
-- Note: This is an automated conversion. Please review for:
--   1. Stored procedures (need manual conversion to PL/pgSQL)
--   2. Triggers (syntax differences)
--   3. Complex constraints
--   4. Application-specific logic

""".format(input_file, __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    sql = header + sql
    
    # Write output
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    converted_size = len(sql)
    
    # Summary
    print("\n" + "="*60)
    print("CONVERSION COMPLETE!")
    print("="*60)
    print(f"Original size:   {original_size:,} bytes")
    print(f"Converted size:  {converted_size:,} bytes")
    print(f"Size difference: {converted_size - original_size:+,} bytes")
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print(f"1. Review the converted file for any issues:")
    print(f"   - Stored procedures need manual conversion")
    print(f"   - Check for any SQL Server-specific features")
    print(f"   - Verify data type conversions")
    print(f"\n2. Import to PostgreSQL:")
    print(f"   psql -U username -d database -f {output_file}")
    print(f"\n3. If you encounter errors during import:")
    print(f"   psql -U username -d database -f {output_file} 2> errors.log")
    print(f"   (Check errors.log for details)")
    print("="*60)

def main():
    """Main function to handle command line arguments"""
    
    # Check arguments
    if len(sys.argv) != 3:
        print("="*60)
        print("SQL Server to PostgreSQL Converter")
        print("="*60)
        print("\nUsage:")
        print("  python convert_sql.py input_file.sql output_file.sql")
        print("\nExample:")
        print("  python convert_sql.py sqlserver_dump.sql postgres_dump.sql")
        print("\nDescription:")
        print("  Converts SQL Server .sql dump files to PostgreSQL format")
        print("  Handles data types, functions, identifiers, and constraints")
        print("="*60)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Validate input file
    if not input_file.lower().endswith('.sql'):
        print(f"Warning: Input file '{input_file}' doesn't have .sql extension")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Check if output file exists
    if os.path.exists(output_file):
        print(f"Warning: Output file '{output_file}' already exists")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    try:
        convert_sqlserver_to_postgres(input_file, output_file)
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"\nError: Permission denied - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: An unexpected error occurred")
        print(f"Details: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
