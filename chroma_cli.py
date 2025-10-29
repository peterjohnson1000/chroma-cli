import chromadb
import json
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to ChromaDB server
chroma_host = os.getenv("CHROMA_HOST")
chroma_port = int(os.getenv("CHROMA_PORT"))
chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

def list_collections():
    """List all collections in the database"""
    collections = chroma_client.list_collections()
    print("\n=== Available Collections ===")
    if not collections:
        print("No collections found.")
        return None
    
    for i, col in enumerate(collections, 1):
        print(f"{i}. {col.name}")
    return collections

def select_collection():
    """Allow user to select a collection"""
    collections = list_collections()
    if not collections:
        return None
    
    while True:
        try:
            choice = input("\nEnter collection number (or name): ").strip()
            
            # Try to parse as number first
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(collections):
                    return chroma_client.get_collection(collections[idx].name)
            
            # Try as collection name
            return chroma_client.get_collection(choice)
        except Exception as e:
            print(f"Error: {e}. Please try again.")

def view_all_documents(collection):
    """View all documents in a collection"""
    print("\n=== Fetching All Documents ===")
    
    # Get collection count
    count = collection.count()
    print(f"Total documents in collection: {count}")
    
    if count == 0:
        print("No documents found.")
        return
    
    # Fetch all documents
    results = collection.get()
    
    print("\n--- Documents ---")
    for i, (doc_id, doc, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas']), 1):
        print(f"\n{i}. ID: {doc_id}")
        print(f"   Document (first 200 chars): {doc[:200]}...")
        if metadata:
            print(f"   Metadata: {json.dumps(metadata, indent=2)}")
        print("-" * 80)

def view_all_ids(collection):
    """View all document IDs in a collection"""
    print("\n=== Document IDs ===")
    
    count = collection.count()
    print(f"Total documents: {count}")
    
    if count == 0:
        print("No documents found.")
        return
    
    results = collection.get()
    
    print("\nIDs:")
    for i, doc_id in enumerate(results['ids'], 1):
        print(f"{i}. {doc_id}")

def delete_document(collection):
    """Delete a specific document by ID"""
    print("\n=== Delete Document ===")
    
    # First show all IDs
    results = collection.get()
    
    if not results['ids']:
        print("No documents to delete.")
        return
    
    print("\nAvailable document IDs:")
    for i, doc_id in enumerate(results['ids'], 1):
        print(f"{i}. {doc_id}")
    
    doc_id = input("\nEnter document ID to delete: ").strip()
    
    if not doc_id:
        print("Cancelled.")
        return
    
    confirm = input(f"Are you sure you want to delete '{doc_id}'? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        try:
            collection.delete(ids=[doc_id])
            print(f"✓ Document '{doc_id}' deleted successfully.")
        except Exception as e:
            print(f"✗ Error deleting document: {e}")
    else:
        print("Cancelled.")

def delete_all_documents(collection):
    """Delete all documents in a collection"""
    print("\n=== Delete All Documents ===")
    
    count = collection.count()
    
    if count == 0:
        print("No documents to delete.")
        return
    
    print(f"Warning: This will delete all {count} documents in the collection.")
    confirm = input("Are you sure? Type 'DELETE ALL' to confirm: ").strip()
    
    if confirm == "DELETE ALL":
        try:
            results = collection.get()
            collection.delete(ids=results['ids'])
            print(f"✓ Successfully deleted all {count} documents.")
        except Exception as e:
            print(f"✗ Error deleting documents: {e}")
    else:
        print("Cancelled.")

def main():
    print("=" * 80)
    print("ChromaDB CLI Tool")
    print(f"Connected to: {chroma_host}:{chroma_port}")
    print("=" * 80)
    
    while True:
        print("\n=== Main Menu ===")
        print("1. Select a collection")
        print("2. List all collections")
        print("3. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            collection = select_collection()
            if collection:
                collection_menu(collection)
        elif choice == "2":
            list_collections()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def collection_menu(collection):
    """Menu for operations on a specific collection"""
    while True:
        print(f"\n=== Collection: {collection.name} ===")
        print(f"Document count: {collection.count()}")
        print("\n1. View all documents")
        print("2. View all document IDs")
        print("3. Delete a document")
        print("4. Delete all documents")
        print("5. Back to main menu")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            view_all_documents(collection)
        elif choice == "2":
            view_all_ids(collection)
        elif choice == "3":
            delete_document(collection)
        elif choice == "4":
            delete_all_documents(collection)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
