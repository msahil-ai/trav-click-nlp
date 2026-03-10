import subprocess
import sys
import time

def run_step(command, step_name):
    print(f"\n>>>>>> STARTING: {step_name} \n")

    result = subprocess.run(
        [sys.executable] + command,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"\n... ERROR in {step_name}")
        print(result.stderr)
        sys.exit(1)

    print(f"\n>>>>>> COMPLETED: {step_name}\n")


if __name__ == "__main__":
    # Step 1: Fetch emails + extract JSON
    run_step(
        ["fetcher_inference_batch_gpt.py"],
        "Email Fetching & Inference"
    )
    start_time = time.time()

    # Step 2: Embed packages into Vector DB
    run_step(
        ["embed_DB.py"],
        "Embedding Database Creation"
    )

    # Step 3: Run RAG pipeline & send recommendation
    run_step(
        ["rag_pipeline.py"],
        "RAG Recommendation Pipeline"
    )

    print("\n>>>> ALL PIPELINE STEPS COMPLETED SUCCESSFULLY.")
    end_time = time.time()
    print(f"Total time taken for the entire pipeline: {end_time - start_time:.2f} seconds")