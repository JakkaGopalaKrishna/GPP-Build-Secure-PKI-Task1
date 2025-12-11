import requests

def request_seed(student_id: str, github_repo_url: str, api_url: str):
    """
    Request encrypted seed from instructor API.
    """

    # 1. Read student public key from PEM file (DO NOT modify formatting)
    with open("keys/student_public.pem", "r") as f:
        public_key = f.read()

    # 2. Prepare HTTP POST request payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key   # <-- KEEP AS IS
    }

    # 3. Send POST request
    headers = {"Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers, timeout=15)

    # 4. Parse JSON response
    if response.status_code != 200:
        raise RuntimeError(f"API error {response.status_code}: {response.text}")

    data = response.json()
    print(data,response)
    encrypted_seed = data.get("encrypted_seed")

    if not encrypted_seed:
        raise RuntimeError("encrypted_seed not found in API response")

    # 5. Save encrypted seed to file
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("encrypted_seed saved to encrypted_seed.txt")


# Example call
if __name__ == "__main__":
    request_seed(
        student_id='22mh1a4296',
        github_repo_url="https://github.com/JakkaGopalaKrishna/GPP-Build-Secure-PKI-Task1.git",
        api_url="https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/",
    )