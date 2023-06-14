# HOW TO USE, DELETE THIS FILE AFTER CHANGES IMPLEMENTED

**First request the ML Ops team to give your repository access to the github-ci-sa service account.**

## Now, consider which products you need:
### I need to share common code between my cloud function and some other service in this repo in a library
`<This section will be added when cloud function and library templates are added>`
### I don't need to share common code between services, I just need a cloud function
`<This section will be added when cloud function and library templates are added>`
### I don't need to share common code between services, I just need a batch service
Raise an initial PR with minimal changes to the template.
Raises a second PR with the relevant changes described here.

## Okay I've pushed my template code, now what?
You now need to make changes to the service before we can get your service into dev.

### General changes everyone should make:
- Update the root README with relevant information/diagrams for your product.
- Add yourself to the `CODEOWNERS` as well as the team leads.
- Set a [repo level environment variable](https://docs.github.com/en/actions/learn-github-actions/variables#creating-configuration-variables-for-a-repository) for 'ML_PRODUCT' e.g. 'ML_PRODUCT=sentiments'
  (requires admin access to repo)

### Cloud Function related changes you need to make (if applicable):
`<This section will be added when cloud function and library templates are added>`
### Library related changes you need to make (if applicable):
`<This section will be added when cloud function and library templates are added>`
### Batch service related changes you need to make (if applicable):

- In `.github/workflows/batch_test_and_deploy.yaml`:
  - Modify the root level environment variables:
    - `PYTHON_VERSION` (to be used for docker container/running tests)
    - `WORKFLOW_SOURCE` (to be either inference-workflow.yaml or scheduled-workflow.yaml depending on use case)
    - `IDENTIFIER` (the format is `batch-{ML_PRODUCT}-{inference/scheduled}`)
- In `src/batch`:
  - Update the README.md file for any relevant information for your batch service
  - Add sample input to your batch process in `input_file_example.jsonl` (or delete for scheduled use case)
  - Add sample output from your batch process in `output_file_example.jsonl` (or delete for scheduled use case)
  - Delete the workflow that you don't need (scheduled/inference)
  - Delete the architecture diagram that you don't need from the `README.md`
  - Update the batch job spec in `src/batch/{inference/scheduled}-workflow.yaml`
    - Update batchJob sub-workflow with your requirements (e.g. GPU, machine type, disk etc.)
    - Update maximum retry in `defineGlobals` step
    - Remove GPU related lines if CPU only in `batchJob` subworkflow (see TODOs in subworkflow)
- In `src/batch/app/`:
  - Write the core logic of your batch app in main.py
  - Update `config.yaml` with configuration to your needs. In the batch process 
    template, the input file is read in chunks, each chunk is then processed and 
    appended 
    to the output file, which is then finally uploaded to GCS. This chunk size is 
    specified by the `batch_processing_size` configuration parameter. If you wish to 
    implement similar chunk-based processing, please update this parameter to your 
    use-case
  - Update Dockerfile as follows:
    - Use `python:3.10` as base image for CPU-only batch process
    - Use `nvcr.io/nvidia/nemo:1.6.1` as base image if GPU usage is also required
  - Update `model_types.py` with Pydantic classes for data validation in your code
  - Update `requirements.txt`
  - Write the tests for the code you wrote above in `tests/`
  - Update the `requirements.txt` in `tests/` if needed

**Request the infrastructure specified in [src/batch/README.md](src/batch/README.md#creating-the-necessary-infrastructure) to be created for you in dev**