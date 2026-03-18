import json

CONTROL_MAPPINGS = {
    "authentication_change": [
        "SOC2-CC6.1",
        "ISO27001-A.9.4.2",
        "PCI-DSS-8.2",
    ],
    "encryption_change": [
        "SOC2-CC6.7",
        "ISO27001-A.10.1.1",
        "PCI-DSS-4.1",
    ],
    "dependency_vulnerability": [
        "SOC2-CC7.1",
        "ISO27001-A.12.6.1",
        "PCI-DSS-6.3.3",
    ],
    "access_control_change": [
        "SOC2-CC6.3",
        "ISO27001-A.9.2.6",
        "PCI-DSS-7.2",
    ],
}

def map_finding(finding):
    return {
        "finding": finding,
        "mapped_controls": CONTROL_MAPPINGS.get(finding.get("evidence_type", ""), [])
    }

if __name__ == "__main__":
    print("Mapper agent running")
