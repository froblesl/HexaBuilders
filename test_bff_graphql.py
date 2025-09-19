"""
Script de prueba para el BFF Web con GraphQL.
Demuestra cómo usar las queries y mutations.
"""

import asyncio
import httpx
import json
from datetime import datetime


# URL del BFF
BFF_URL = "http://localhost:8000/api/v1/graphql"


async def test_graphql_query(query: str, variables: dict = None):
    """Ejecuta una query GraphQL"""
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            BFF_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return response.json()


async def test_health_check():
    """Prueba el health check"""
    print("🔍 Testing Health Check...")
    
    query = """
    query {
        health {
            service
            status
            pattern
            sagaTypes
            eventDispatcher
            timestamp
        }
    }
    """
    
    result = await test_graphql_query(query)
    print("✅ Health Check Result:")
    print(json.dumps(result, indent=2, default=str))


async def test_start_partner_onboarding():
    """Prueba iniciar onboarding de partner"""
    print("\n🚀 Testing Start Partner Onboarding...")
    
    mutation = """
    mutation StartPartnerOnboarding($input: PartnerOnboardingInput!) {
        startPartnerOnboarding(input: $input) {
            success
            message
            partnerId
            timestamp
        }
    }
    """
    
    variables = {
        "input": {
            "partnerData": {
                "nombre": "TechSolutions Inc",
                "email": "contact@techsolutions.com",
                "telefono": "+1234567890",
                "tipoPartner": "EMPRESA",
                "preferredContractType": "PREMIUM",
                "requiredDocuments": ["IDENTITY", "BUSINESS_REGISTRATION"]
            },
            "correlationId": f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    }
    
    result = await test_graphql_query(mutation, variables)
    print("✅ Start Partner Onboarding Result:")
    print(json.dumps(result, indent=2, default=str))
    
    # Retornar partner_id para pruebas posteriores
    if result.get("data", {}).get("startPartnerOnboarding", {}).get("success"):
        return result["data"]["startPartnerOnboarding"]["partnerId"]
    return None


async def test_get_saga_status(partner_id: str):
    """Prueba obtener estado de saga"""
    print(f"\n📊 Testing Get Saga Status for partner: {partner_id}...")
    
    query = """
    query GetSagaStatus($partnerId: String!) {
        sagaStatus(partnerId: $partnerId) {
            partnerId
            sagaType
            status
            completedSteps
            failedSteps
            createdAt
            updatedAt
            correlationId
            steps {
                stepName
                status
                startedAt
                completedAt
                errorMessage
            }
        }
    }
    """
    
    variables = {"partnerId": partner_id}
    result = await test_graphql_query(query, variables)
    print("✅ Get Saga Status Result:")
    print(json.dumps(result, indent=2, default=str))


async def test_compensate_saga(partner_id: str):
    """Prueba compensar saga"""
    print(f"\n🔄 Testing Compensate Saga for partner: {partner_id}...")
    
    mutation = """
    mutation CompensateSaga($partnerId: String!, $input: CompensationInput!) {
        compensateSaga(partnerId: $partnerId, input: $input) {
            success
            message
            partnerId
            timestamp
        }
    }
    """
    
    variables = {
        "partnerId": partner_id,
        "input": {
            "reason": "Test compensation request"
        }
    }
    
    result = await test_graphql_query(mutation, variables)
    print("✅ Compensate Saga Result:")
    print(json.dumps(result, indent=2, default=str))


async def test_schema_introspection():
    """Prueba la introspección del schema"""
    print("\n🔍 Testing Schema Introspection...")
    
    query = """
    query IntrospectionQuery {
        __schema {
            queryType {
                name
                fields {
                    name
                    description
                    type {
                        name
                    }
                }
            }
            mutationType {
                name
                fields {
                    name
                    description
                    type {
                        name
                    }
                }
            }
        }
    }
    """
    
    result = await test_graphql_query(query)
    print("✅ Schema Introspection Result:")
    print(json.dumps(result, indent=2, default=str))


async def main():
    """Función principal de prueba"""
    print("🧪 Starting BFF GraphQL Tests...")
    print("=" * 50)
    
    try:
        # 1. Health Check
        await test_health_check()
        
        # 2. Schema Introspection
        await test_schema_introspection()
        
        # 3. Start Partner Onboarding
        partner_id = await test_start_partner_onboarding()
        
        if partner_id:
            # 4. Get Saga Status
            await test_get_saga_status(partner_id)
            
            # 5. Compensate Saga (opcional)
            # await test_compensate_saga(partner_id)
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
