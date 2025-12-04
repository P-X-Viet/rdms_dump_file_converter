#!/usr/bin/env python3
"""
Enhanced SQL Server to PostgreSQL SQL Dump Converter
Handles complex SQL Server syntax including constraints, indexes, and more
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
    print("\n[1/12] Removing SQL Server specific commands...")
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
    print("[2/12] Converting identifier syntax [name] to \"name\"...")
    sql = re.sub(r'\[([^\]]+)\]', r'"\1"', sql)
    
    # ===== STEP 3: Handle IDENTITY columns (before data type conversion) =====
    print("[3/12] Converting IDENTITY columns...")
    # INT IDENTITY(1,1) NOT NULL -> SERIAL NOT NULL
    sql = re.sub(r'\bINT\s+IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)\s+NOT\s+NULL', 'SERIAL NOT NULL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bBIGINT\s+IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)\s+NOT\s+NULL', 'BIGSERIAL NOT NULL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSMALLINT\s+IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)\s+NOT\s+NULL', 'SMALLSERIAL NOT NULL', sql, flags=re.IGNORECASE)
    
    # INT IDENTITY(1,1) -> SERIAL
    sql = re.sub(r'\bINT\s+IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)', 'SERIAL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bBIGINT\s+IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)', 'BIGSERIAL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSMALLINT\s+IDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)', 'SMALLSERIAL', sql, flags=re.IGNORECASE)
    
    # INT IDENTITY -> SERIAL
    sql = re.sub(r'\bINT\s+IDENTITY\b', 'SERIAL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bBIGINT\s+IDENTITY\b', 'BIGSERIAL', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSMALLINT\s+IDENTITY\b', 'SMALLSERIAL', sql, flags=re.IGNORECASE)
    
    # ===== STEP 4: Convert Data Types =====
    print("[4/12] Converting data types...")
    
    # String types
    sql = re.sub(r'\bNVARCHAR\s*\(\s*MAX\s*\)', 'TEXT', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bVARCHAR\s*\(\s*MAX\s*\)', 'TEXT', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNVARCHAR\s*\(', 'VARCHAR(', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNVARCHAR\b', 'VARCHAR', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNVARCHAR2\b', 'VARCHAR', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNCHAR\s*\(', 'CHAR(', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNTEXT\b', 'TEXT', sql, flags=re.IGNORECASE)
    
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
    
    # ===== STEP 5: Remove CLUSTERED/NONCLUSTERED Keywords =====
    print("[5/12] Removing CLUSTERED/NONCLUSTERED keywords...")
    sql = re.sub(r'\bCLUSTERED\s+', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNONCLUSTERED\s+', '', sql, flags=re.IGNORECASE)
    
    # ===== STEP 6: Handle PRIMARY KEY Constraints =====
    print("[6/12] Converting PRIMARY KEY constraints...")
    # Remove constraint names before PRIMARY KEY
    sql = re.sub(r'CONSTRAINT\s+"[^"]+"\s+PRIMARY\s+KEY', 'PRIMARY KEY', sql, flags=re.IGNORECASE)
    
    # ===== STEP 7: Handle WITH clauses in constraints =====
    print("[7/12] Removing WITH clauses from constraints...")
    # Remove WITH (PAD_INDEX = ..., STATISTICS_NORECOMPUTE = ..., etc.)
    sql = re.sub(r'WITH\s*\([^)]*PAD_INDEX[^)]*\)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\([^)]*STATISTICS_NORECOMPUTE[^)]*\)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\([^)]*IGNORE_DUP_KEY[^)]*\)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\([^)]*ALLOW_ROW_LOCKS[^)]*\)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\([^)]*ALLOW_PAGE_LOCKS[^)]*\)\s*', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\([^)]*FILLFACTOR[^)]*\)\s*', '', sql, flags=re.IGNORECASE)
    
    # ===== STEP 8: Handle ON [PRIMARY] clauses =====
    print("[8/12] Removing ON [PRIMARY] and filegroup clauses...")
    sql = re.sub(r'\s+ON\s+"PRIMARY"\s*', ' ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+ON\s+PRIMARY\s*', ' ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+ON\s+\[PRIMARY\]\s*', ' ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+TEXTIMAGE_ON\s+"PRIMARY"\s*', ' ', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\s+TEXTIMAGE_ON\s+\[PRIMARY\]\s*', ' ', sql, flags=re.IGNORECASE)
    
    # ===== STEP 9: Convert Functions =====
    print("[9/12] Converting functions...")
    
    # Date functions
    sql = re.sub(r'\bGETDATE\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bGETUTCDATE\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSYSDATETIME\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bSYSDATETIMEOFFSET\s*\(\s*\)', 'CURRENT_TIMESTAMP', sql, flags=re.IGNORECASE)
    
    # String functions
    sql = re.sub(r'\bLEN\s*\(', 'LENGTH(', sql, flags=re.IGNORECASE)
    
    # NULL handling
    sql = re.sub(r'\bISNULL\s*\(', 'COALESCE(', sql, flags=re.IGNORECASE)
    
    # GUID/UUID
    sql = re.sub(r'\bNEWID\s*\(\s*\)', 'gen_random_uuid()', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bNEWSEQUENTIALID\s*\(\s*\)', 'gen_random_uuid()', sql, flags=re.IGNORECASE)
    
    # ===== STEP 10: Remove Query Hints =====
    print("[10/12] Removing query hints...")
    sql = re.sub(r'WITH\s*\(\s*NOLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*READUNCOMMITTED\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*ROWLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*UPDLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*HOLDLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    sql = re.sub(r'WITH\s*\(\s*TABLOCK\s*\)', '', sql, flags=re.IGNORECASE)
    
    # ===== STEP 11: Convert Default Constraints =====
    print("[11/12] Converting default constraints...")
    # Remove constraint names from defaults
    sql = re.sub(r'CONSTRAINT\s+"[^"]+"\s+DEFAULT\s+', 'DEFAULT ', sql, flags=re.IGNORECASE)
    
    # Convert bit defaults (0/1 to FALSE/TRUE)
    sql = re.sub(r'DEFAULT\s+\(\s*\(\s*0\s*\)\s*\)', 'DEFAULT FALSE', sql, flags=re.IGNORECASE)
    sql = re.sub(r'DEFAULT\s+\(\s*\(\s*1\s*\)\s*\)', 'DEFAULT TRUE', sql, flags=re.IGNORECASE)
    sql = re.sub(r'DEFAULT\s+\(\s*0\s*\)', 'DEFAULT FALSE', sql, flags=re.IGNORECASE)
    sql = re.sub(r'DEFAULT\s+\(\s*1\s*\)', 'DEFAULT TRUE', sql, flags=re.IGNORECASE)
    
    # Remove extra parentheses around defaults
    sql = re.sub(r'DEFAULT\s+\(\s*\(([^)]+)\)\s*\)', r'DEFAULT (\1)', sql, flags=re.IGNORECASE)
    
    # ===== STEP 12: Handle CHECK Constraints =====
    print("[12/12] Converting CHECK constraints...")
    # Remove constraint names from CHECK constraints
    sql = re.sub(r'CONSTRAINT\s+"[^"]+"\s+CHECK\s+', 'CHECK ', sql, flags=re.IGNORECASE)
    
    # Convert (([column]=(0))) to (column = FALSE)
    sql = re.sub(r'CHECK\s+\(\s*\(\s*"([^"]+)"\s*=\s*\(\s*0\s*\)\s*\)\s*\)', r'CHECK ("\1" = FALSE)', sql, flags=re.IGNORECASE)
    sql = re.sub(r'CHECK\s+\(\s*\(\s*"([^"]+)"\s*=\s*\(\s*1\s*\)\s*\)\s*\)', r'CHECK ("\1" = TRUE)', sql, flags=re.IGNORECASE)
    
    # ===== FINAL: Clean Up Formatting =====
    print("\nCleaning up formatting...")
    
    # Clean up multiple semicolons
    sql = re.sub(r';\s*;+', ';', sql)
    
    # Remove excessive blank lines
    sql = re.sub(r'\n\s*\n\s*\n+', '\n\n', sql)
    
    # Remove trailing spaces
    sql = re.sub(r' +\n', '\n', sql)
    
    # Clean up spaces before commas and semicolons
    sql = re.sub(r'\s+,', ',', sql)
    sql = re.sub(r'\s+;', ';', sql)
    
    # Add PostgreSQL header comment
    header = """-- Converted from SQL Server to PostgreSQL
-- Original file: {}
-- Conversion date: {}
-- 
-- IMPORTANT NOTES:
-- 1. Stored procedures require manual conversion to PL/pgSQL
-- 2. Triggers have different syntax in PostgreSQL
-- 3. Some SQL Server features may not have direct PostgreSQL equivalents
-- 4. Review all constraints and indexes carefully
-- 5. Test thoroughly before using in production
--
-- Common remaining issues to check:
-- - Stored procedures and functions
-- - Triggers
-- - Cursors
-- - Complex constraints
-- - Application-specific logic

""".format(input_file, __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    sql = header + sql
    
    # Write output
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    converted_size = len(sql)
    
    # Summary
    print("\n" + "="*70)
    print("CONVERSION COMPLETE!")
    print("="*70)
    print(f"Original size:   {original_size:,} bytes")
    print(f"Converted size:  {converted_size:,} bytes")
    print(f"Size difference: {converted_size - original_size:+,} bytes")
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print(f"1. Review the converted file: {output_file}")
    print(f"   Look for:")
    print(f"   - Stored procedures (need manual conversion)")
    print(f"   - Triggers (different syntax)")
    print(f"   - Any remaining SQL Server-specific syntax")
    print(f"\n2. Import to PostgreSQL:")
    print(f"   psql -U username -d database -f {output_file}")
    print(f"\n3. Capture errors if any:")
    print(f"   psql -U username -d database -f {output_file} 2> errors.log")
    print(f"\n4. Common PostgreSQL commands after import:")
    print(f"   \\dt         - List tables")
    print(f"   \\d+ table   - Describe table structure")
    print(f"   \\di         - List indexes")
    print("="*70)

def main():
    """Main function to handle command line arguments"""
    
    # Check arguments
    if len(sys.argv) != 3:
        print("="*70)
        print("SQL Server to PostgreSQL Converter (Enhanced)")
        print("="*70)
        print("\nUsage:")
        print("  python convert_sql.py input_file.sql output_file.sql")
        print("\nExample:")
        print("  python convert_sql.py sqlserver_dump.sql postgres_dump.sql")
        print("\nDescription:")
        print("  Converts SQL Server .sql dump files to PostgreSQL format")
        print("  Handles: data types, IDENTITY, constraints, indexes, and more")
        print("="*70)
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
