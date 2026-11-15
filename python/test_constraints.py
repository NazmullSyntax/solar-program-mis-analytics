"""
test_constraints.py
-------------------
Test database constraints by attempting bad inserts.
"""
import os
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "solar_program.db")


def test_insert(conn, description, sql, params):
    """Test insert, catch errors."""
    try:
        conn.execute(sql, params)
        conn.commit()
        print(f"   ❌ ALLOWED: {description} (should have failed!)")
    except sqlite3.IntegrityError as e:
        print(f"   ✅ BLOCKED: {description}")
        print(f"      Reason: {e}")


def main():
    print("=" * 60)
    print("  🛡️ CONSTRAINT TESTS")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    try:
        # Test 1: Duplicate primary key
        test_insert(
            conn,
            "Duplicate Customer_ID",
            "INSERT INTO customers (Customer_ID, Customer_Name) VALUES (?, ?)",
            ("CUST-00001", "Test Name")
        )

        # Test 2: Negative capacity
        test_insert(
            conn,
            "Negative Solar Capacity",
            "INSERT INTO installations (Installation_ID, Customer_ID, Solar_Capacity_KW) "
            "VALUES (?, ?, ?)",
            ("INST-TEST", "CUST-00001", -5.0)
        )

        # Test 3: Invalid status
        test_insert(
            conn,
            "Invalid status value",
            "INSERT INTO installations (Installation_ID, Customer_ID, Installation_Status) "
            "VALUES (?, ?, ?)",
            ("INST-TEST2", "CUST-00001", "INVALID_STATUS")
        )

        # Test 4: Orphan foreign key
        test_insert(
            conn,
            "Orphan foreign key",
            "INSERT INTO installations (Installation_ID, Customer_ID) VALUES (?, ?)",
            ("INST-TEST3", "NON-EXISTENT-CUSTOMER")
        )

    finally:
        conn.close()

    print("\n" + "=" * 60)
    print("  🎉 CONSTRAINT TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()