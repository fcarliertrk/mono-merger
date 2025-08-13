# mono-merger

### Overview
- A simple Python script that merges multiple individual GitHub repositories into a single monolith. 
- This script takes in a single YAML configuration file as input, this file tells the script.
    - What repositories to merge.
    - How these different repositories should be grouped together.
    - What branches from a repo should be merged into the monolith.
- Basically, the config file allows the user to specify how to merge these repositories.

### Configuration

#### Sample YAML Configuration
```yaml
repos:
  - url: "https://github.com/org/repo1"
    branches:
      - name: "main"
        domain: "user-management"
      - name: "payment-service"
        services: ["payment-api"]
        domain: "payment"
        
  - url: "https://github.com/org/repo2"
    branches:
      - name: "analytics-branch"
        domain: "analytics"

domain_mapping:
  user-management: "domains/user-management"
  payment: "domains/payment"
  analytics: "domains/analytics"

output_dir: "/Users/felipezunigacarlier/projects/manuf-mono-repo"
```
