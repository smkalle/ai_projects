# API Specification - Rare Disease Drug Repurposing AI

## 📋 Overview

RESTful API for the Rare Disease Drug Repurposing AI System, providing programmatic access to drug repurposing analysis, biomedical research, and citation-verified recommendations.

**Base URL**: `https://api.raredrug.ai/v1`  
**Authentication**: Bearer Token (API Key)  
**Content-Type**: `application/json`  
**Rate Limits**: 1000 requests/hour (authenticated), 100 requests/hour (unauthenticated)

## 🔐 Authentication

```bash
# Include API key in header
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.raredrug.ai/v1/analyze
```

## 📊 Core Endpoints

### 1. **Drug Repurposing Analysis**

#### `POST /analyze/repurposing`

Analyze a rare disease for drug repurposing opportunities.

**Request Body:**
```json
{
  "disease": {
    "name": "Hutchinson-Gilford Progeria Syndrome",
    "omim_id": "176670",
    "orphanet_id": "740",
    "description": "Rare genetic disorder causing accelerated aging"
  },
  "patient_profile": {
    "age": 12,
    "weight_kg": 25,
    "sex": "male",
    "genetic_variants": ["LMNA:c.1824C>T"],
    "symptoms": [
      "growth retardation",
      "cardiovascular complications",
      "alopecia",
      "joint stiffness"
    ],
    "current_medications": [],
    "allergies": [],
    "comorbidities": []
  },
  "analysis_parameters": {
    "include_experimental": false,
    "confidence_threshold": 0.7,
    "max_results": 10,
    "prioritize_safety": true,
    "geographic_restrictions": ["FDA", "EMA"],
    "exclude_contraindicated": true
  }
}
```

**Response:**
```json
{
  "request_id": "req_1234567890",
  "status": "completed",
  "timestamp": "2024-12-18T10:30:00Z",
  "processing_time_ms": 15420,
  "results": {
    "drug_candidates": [
      {
        "drug": {
          "name": "Lonafarnib",
          "drugbank_id": "DB05294",
          "generic_name": "lonafarnib",
          "brand_names": ["Zokinvy"],
          "atc_code": "L01XX52",
          "chemical_formula": "C27H31Br2N3O2",
          "molecular_weight": 589.37,
          "smiles": "CC(C)(C)c1ccc(cc1)C(=O)N2CCN(CC2)c3nc(nc(n3)N4CCN(CC4)C(=O)c5ccc(cc5)C(C)(C)C)Br"
        },
        "repurposing_analysis": {
          "confidence_score": 0.89,
          "mechanism_of_action": "Farnesyltransferase inhibitor that prevents abnormal protein prenylation",
          "target_pathway": "Protein prenylation cascade",
          "expected_benefit": "Reduces progerin accumulation and cellular aging",
          "evidence_strength": "strong",
          "regulatory_status": {
            "fda_approved": true,
            "indication": "Hutchinson-Gilford Progeria Syndrome",
            "approval_date": "2020-11-20",
            "orphan_designation": true
          }
        },
        "safety_profile": {
          "known_side_effects": [
            "nausea",
            "vomiting", 
            "decreased appetite",
            "fatigue"
          ],
          "contraindications": ["pregnancy", "severe hepatic impairment"],
          "drug_interactions": ["strong CYP3A4 inhibitors"],
          "monitoring_requirements": ["liver function", "complete blood count"],
          "pediatric_safety": "established"
        },
        "dosing_recommendations": {
          "pediatric_dose": "150 mg/m2 twice daily",
          "adult_dose": "300 mg twice daily",
          "adjustment_factors": ["weight", "surface_area", "hepatic_function"],
          "administration": "oral, with food"
        },
        "citations": [
          {
            "id": "pmid_32436818",
            "title": "Lonafarnib for Hutchinson-Gilford progeria syndrome",
            "authors": ["Merideth MA", "Gordon LB", "Clauss S"],
            "journal": "N Engl J Med",
            "year": 2008,
            "volume": 358,
            "pages": "2682-2690",
            "doi": "10.1056/NEJMoa0706898",
            "evidence_level": 2,
            "study_type": "clinical_trial"
          }
        ]
      }
    ],
    "summary": {
      "total_candidates": 5,
      "high_confidence": 2,
      "moderate_confidence": 3,
      "experimental_only": 0,
      "safety_concerns": 1
    },
    "research_gaps": [
      "Limited pediatric safety data for combination therapies",
      "Long-term cardiovascular outcomes not well studied",
      "Optimal dosing for different LMNA mutations unclear"
    ]
  },
  "citations": {
    "total_sources": 47,
    "pubmed_articles": 35,
    "clinical_trials": 8,
    "regulatory_documents": 4,
    "quality_score": 8.7
  }
}
```

### 2. **Literature Search**

#### `GET /search/literature`

Search biomedical literature with advanced filtering.

**Query Parameters:**
- `q` (required): Search query
- `databases`: Comma-separated list (pubmed,drugbank,clinicaltrials)
- `date_from`: ISO date (YYYY-MM-DD)
- `date_to`: ISO date (YYYY-MM-DD)
- `study_types`: Comma-separated (rct,meta_analysis,case_study)
- `evidence_level`: Integer 1-5
- `limit`: Integer 1-100 (default: 20)
- `offset`: Integer (default: 0)

**Example Request:**
```bash
GET /search/literature?q=progeria+lonafarnib&databases=pubmed&study_types=rct&evidence_level=1,2&limit=10
```

**Response:**
```json
{
  "query": "progeria lonafarnib",
  "total_results": 156,
  "returned_count": 10,
  "results": [
    {
      "id": "pmid_32436818",
      "source": "pubmed",
      "title": "Effect of lonafarnib on cardiac function in Hutchinson-Gilford progeria syndrome",
      "authors": ["Ullrich NJ", "Silvera VM", "Campbell SE"],
      "abstract": "Background: Hutchinson-Gilford progeria syndrome (HGPS) is characterized by...",
      "journal": "Circulation",
      "publication_date": "2013-03-15",
      "doi": "10.1161/CIRCULATIONAHA.112.000543",
      "pmid": "23444100",
      "study_type": "clinical_trial",
      "evidence_level": 2,
      "mesh_terms": ["Progeria", "Farnesyltransferase Inhibitors", "Heart Function"],
      "relevance_score": 0.94
    }
  ],
  "facets": {
    "study_types": {
      "clinical_trial": 45,
      "observational": 32,
      "case_study": 28,
      "review": 51
    },
    "publication_years": {
      "2020-2024": 67,
      "2015-2019": 45,
      "2010-2014": 31,
      "2005-2009": 13
    }
  }
}
```

### 3. **Drug Information**

#### `GET /drugs/{drug_id}`

Get comprehensive information about a specific drug.

**Path Parameters:**
- `drug_id`: DrugBank ID (e.g., DB05294) or generic name

**Response:**
```json
{
  "drug": {
    "drugbank_id": "DB05294",
    "name": "Lonafarnib",
    "generic_name": "lonafarnib",
    "brand_names": ["Zokinvy"],
    "description": "Lonafarnib is a farnesyltransferase inhibitor...",
    "chemical_info": {
      "formula": "C27H31Br2N3O2",
      "molecular_weight": 589.37,
      "smiles": "CC(C)(C)c1ccc(cc1)C(=O)N2CCN(CC2)c3nc(nc(n3)N4CCN(CC4)C(=O)c5ccc(cc5)C(C)(C)C)Br",
      "inchi": "InChI=1S/C27H31Br2N3O2/c1-26(2,3)19-7-11-21(12-8-19)25(34)32-15-17-31(18-16-32)24-30-22(28)29-23(29-24)33-13-9-20(10-14-33)27(4,5)6/h7-12H,13-18H2,1-6H3",
      "cas_number": "193275-84-2"
    },
    "pharmacology": {
      "mechanism": "Inhibits farnesyltransferase enzyme",
      "targets": ["Protein farnesyltransferase subunit beta"],
      "absorption": "Well absorbed orally",
      "metabolism": "Hepatic via CYP3A4",
      "half_life": "4.5 hours",
      "excretion": "Primarily fecal"
    },
    "indications": [
      {
        "condition": "Hutchinson-Gilford Progeria Syndrome",
        "approval_status": "approved",
        "fda_approval_date": "2020-11-20",
        "orphan_designation": true
      }
    ],
    "contraindications": [
      "Pregnancy",
      "Severe hepatic impairment",
      "Hypersensitivity to lonafarnib"
    ],
    "interactions": [
      {
        "drug": "Ketoconazole",
        "severity": "major",
        "mechanism": "CYP3A4 inhibition increases lonafarnib levels"
      }
    ]
  }
}
```

### 4. **Disease Information**

#### `GET /diseases/{disease_id}`

Get comprehensive information about a rare disease.

**Path Parameters:**
- `disease_id`: OMIM ID, Orphanet ID, or disease name

**Response:**
```json
{
  "disease": {
    "omim_id": "176670",
    "orphanet_id": "740",
    "name": "Hutchinson-Gilford Progeria Syndrome",
    "synonyms": ["HGPS", "Progeria", "Premature aging syndrome"],
    "description": "A rare genetic disorder characterized by accelerated aging...",
    "genetics": {
      "inheritance_pattern": "autosomal_dominant",
      "associated_genes": [
        {
          "gene_symbol": "LMNA",
          "gene_name": "Lamin A/C",
          "mutations": ["c.1824C>T (p.Gly608Gly)"],
          "pathogenicity": "pathogenic"
        }
      ]
    },
    "epidemiology": {
      "prevalence": "1 in 4-8 million births",
      "geographic_distribution": "worldwide",
      "age_of_onset": "birth to 2 years"
    },
    "clinical_features": [
      {
        "feature": "Growth retardation",
        "frequency": "100%",
        "onset": "early_childhood"
      },
      {
        "feature": "Cardiovascular disease",
        "frequency": "90%",
        "onset": "childhood"
      }
    ],
    "treatments": [
      {
        "drug": "Lonafarnib",
        "approval_status": "approved",
        "evidence_level": "strong"
      }
    ],
    "prognosis": {
      "life_expectancy": "13-16 years",
      "major_complications": ["cardiovascular disease", "stroke"]
    }
  }
}
```

### 5. **Citation Verification**

#### `POST /citations/verify`

Verify and format citations according to medical standards.

**Request Body:**
```json
{
  "citations": [
    {
      "pmid": "32436818",
      "doi": "10.1056/NEJMoa0706898"
    }
  ],
  "format": "vancouver"
}
```

**Response:**
```json
{
  "verified_citations": [
    {
      "id": "pmid_32436818",
      "verification_status": "verified",
      "formatted_citation": "Merideth MA, Gordon LB, Clauss S, et al. Lonafarnib for Hutchinson-Gilford progeria syndrome. N Engl J Med. 2008;358(26):2682-2690. doi:10.1056/NEJMoa0706898",
      "metadata": {
        "journal_impact_factor": 91.245,
        "publication_type": "clinical_trial",
        "evidence_level": 2,
        "retraction_status": "not_retracted",
        "last_verified": "2024-12-18T10:30:00Z"
      }
    }
  ]
}
```

## 🔄 Asynchronous Operations

### Long-Running Analysis

For complex analyses that take >30 seconds:

#### `POST /analyze/repurposing/async`

**Response:**
```json
{
  "job_id": "job_abc123",
  "status": "queued",
  "estimated_completion": "2024-12-18T10:35:00Z"
}
```

#### `GET /jobs/{job_id}`

**Response:**
```json
{
  "job_id": "job_abc123",
  "status": "completed",
  "progress": 100,
  "created_at": "2024-12-18T10:30:00Z",
  "completed_at": "2024-12-18T10:34:15Z",
  "result_url": "/analyze/repurposing/results/job_abc123"
}
```

## 📊 Status and Health Endpoints

### `GET /health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-12-18T10:30:00Z",
  "services": {
    "database": "healthy",
    "vector_store": "healthy",
    "external_apis": {
      "pubmed": "healthy",
      "drugbank": "healthy",
      "pubchem": "healthy"
    }
  }
}
```

### `GET /metrics`

```json
{
  "requests_per_hour": 1247,
  "average_response_time_ms": 890,
  "cache_hit_rate": 0.78,
  "api_quotas": {
    "pubmed": {
      "used": 234,
      "limit": 10000,
      "reset_time": "2024-12-18T11:00:00Z"
    }
  }
}
```

## ⚠️ Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "INVALID_DISEASE_ID",
    "message": "The provided disease ID is not recognized",
    "details": {
      "provided_id": "invalid123",
      "suggestion": "Use OMIM or Orphanet IDs"
    },
    "timestamp": "2024-12-18T10:30:00Z",
    "request_id": "req_1234567890"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_API_KEY` | 401 | API key is missing or invalid |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INVALID_DISEASE_ID` | 400 | Disease identifier not found |
| `INSUFFICIENT_DATA` | 422 | Not enough data for analysis |
| `EXTERNAL_API_ERROR` | 503 | Upstream service unavailable |
| `SAFETY_CONCERN` | 200 | Analysis completed with safety warnings |

## 🛡️ Safety Disclaimers

All API responses include mandatory medical disclaimers:

```json
{
  "medical_disclaimer": {
    "text": "This information is for research purposes only and should not be used as a substitute for professional medical advice.",
    "last_updated": "2024-12-18T00:00:00Z",
    "regulatory_notice": "Drug recommendations require healthcare provider evaluation and may not be approved for all jurisdictions."
  }
}
```

## 📚 SDK and Integration

### Python SDK Example

```python
from rare_disease_ai import RareDiseaseAPI

client = RareDiseaseAPI(api_key="your_api_key")

# Analyze drug repurposing
result = client.analyze_repurposing(
    disease_name="Hutchinson-Gilford Progeria Syndrome",
    patient_profile={
        "age": 12,
        "symptoms": ["growth retardation", "cardiovascular complications"]
    }
)

print(f"Found {len(result.drug_candidates)} potential drugs")
for drug in result.drug_candidates:
    print(f"- {drug.name}: {drug.confidence_score:.2f}")
```

This API specification provides comprehensive access to the rare disease drug repurposing system while maintaining medical safety standards and citation integrity.