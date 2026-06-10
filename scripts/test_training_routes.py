import json
import urllib.request
import urllib.error

def run_tests():
    # 1. Test GET /training
    try:
        req = urllib.request.urlopen("http://127.0.0.1:5001/training")
        html = req.read().decode('utf-8')
        print("GET /training returned status 200")
        assert "Training Data Correction" in html, "Page title not found in HTML"
        print("HTML validation: Title exists in page.")
    except Exception as e:
        print("GET /training failed:", e)
        return

    # Load initial manifest state to choose an item
    manifest_path = "/Users/charlesmcvicker/code/phoenix/training_data/manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Grab the first item
    first_key = list(manifest.keys())[0]
    original_item = manifest[first_key]
    print(f"Testing update on item ID: {first_key}")
    print(f"Original status: {original_item.get('status')}, label: {original_item.get('label')}")

    # 2. Test POST /training/update
    try:
        url = "http://127.0.0.1:5001/training/update"
        data = json.dumps({
            "id": first_key,
            "status": "labeled",
            "label": "ᎠᏎ ᎤᏂᎪᎯ (Test Update)"
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req)
        res_data = json.loads(response.read().decode('utf-8'))
        print("POST /training/update response:", res_data)
        assert res_data.get("success") is True, "Success should be True"

        # Verify change in local manifest file
        with open(manifest_path, "r", encoding="utf-8") as f:
            updated_manifest = json.load(f)
        
        updated_item = updated_manifest[first_key]
        print(f"Updated status: {updated_item.get('status')}, label: {updated_item.get('label')}")
        assert updated_item.get("status") == "labeled"
        assert updated_item.get("label") == "ᎠᏎ ᎤᏂᎪᎯ (Test Update)"
        print("Verification successful: manifest.json is updated on disk!")

        # Revert change to keep training data clean
        revert_data = json.dumps({
            "id": first_key,
            "status": original_item.get("status", "unlabeled"),
            "label": original_item.get("label", "")
        }).encode('utf-8')
        req = urllib.request.Request(url, data=revert_data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
        print("Reverted the test item changes successfully.")

    except Exception as e:
        print("POST /training/update failed:", e)

if __name__ == "__main__":
    run_tests()
