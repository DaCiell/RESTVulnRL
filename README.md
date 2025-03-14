# RESTVulnRL

A reinforcement learning-based vulnerability detection method for RESTful APIs. RESTVulnRL integrates reinforcement learning algorithms into the fuzz testing process to overcome the shortcomings of conventional approaches in handling complex parameter dependencies and multi-step interaction scenarios. By inferring parameter generation strategies and dependency relationships, the method constructs high-quality test sequences. It further combines validation server monitoring and response content clustering analysis to achieve multi-dimensional vulnerability coverage.

## How to Use RESTVulnRL

### Dependencies Installation

    pip install -r requirements.txt

### OpenAPI Specification Parsing

First, convert the application's OAS to version 3.0 in YAML format. You can use the tool [Swagger Editor](https://editor.swagger.io/).

RESTVulnRL provides 3 scripts to preprocess the OpenAPI Specification (OAS) as follows:

- **`swagger_nullable.py`**  
  This script removes `nullable` fields from the OAS file. It recursively traverses the entire OAS file, deletes all `nullable` related fields, and saves the processed content to the specified output file to avoid `nullable` affecting the API parsing or testing.

- **`swagger_ref.py`**  
  This script parses the `$ref` references in the OAS file and expands them into concrete definitions. It recursively parses the paths pointed to by `$ref`, replaces the `$ref` structure, prevents parsing issues caused by nested references, and checks for potential circular references.

- **`swagger_security.py`**  
  This script converts the `security` definitions in the OAS file into `parameters`. For APIs using API Key authentication, the script converts the `security` rules into standard request parameters so that the testing tool can correctly recognize and use the authentication information for testing.

Before parsing, it is recommended to place your OAS file in the `/OAS` directory and perform the following processing:

```bash
    python swagger_nullable.py OAS/openapi.yaml OAS/openapi.yaml
    python swagger_ref.py OAS/openapi.yaml OAS/openapi.yaml
    python swagger_security.py OAS/openapi.yaml OAS/openapi.yaml
```

RESTVulnRL uses RESTLer to assist in OAS parsing, and the usage is as follows:

    cd restler_bin/restler
    restler.exe compile --api_spec ../../OAS/openapi.yaml

If parsing is successful, a "Compile" directory will be generated under the `restler_bin/restler` directory.

### Successful Requests Construction

First, deploy the MongoDB and Redis servers. You can set the database-related information in the `config.py` file.

Then, use `construct.py` to construct successful requests:

    python construct.py restler_bin/restler/Compile/grammar.json OAS/openapi.yaml <url>

Where `<url>` is the address of the API application.

The testing process will generate a log with the current time in the `/logs` directory. After the test is complete, corresponding request records will be generated in MongoDB.

### Vulnerability Detection

To perform vulnerability detection, you need to first deploy a validation server to listen for the requests forwarded by the API application.

You also need to download the text8 model：

    https://drive.google.com/drive/folders/1VljwWp-qMCt4zbdAKufJ6ApE2PpOfGvk?usp=sharing

Use `detect.py` to detect vulnerabilities:

    python detect.py <url> <validation_ip>

Where `<url>` is the address of the API application, and `<validation_ip>` is the address of the validation server.

Similarly, the testing process will generate a log with the current time in the `/logs` directory. After the test is complete, corresponding request records will be generated in MongoDB.

