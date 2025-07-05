from embedding import get_embedding
from opensearch_client import get_opensearch_client


def keyword_search(query_text, top_k=20):
    """
    Perform keyword search using OpenSearch.

    Args:
        query_text (str): The query text to search for
        top_k (int): Number of results to return

    Returns:
        list: Search results
    """
    client = get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        search_query = {
            "size": top_k,
            "query": {"match": {"abstract": query_text}},
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }

        response = client.search(index=index_name, body=search_query)
        return response["hits"]["hits"]
    except Exception as e:
        print(f"Keyword search error: {e}")
        return []
    
def semantic_search(query_text, top_k=20):
    """
    Perform semantic search using vector embeddings.

    Args:
        query_text (str): The query text to search for
        top_k (int): Number of results to return

    Returns:
        list: Search results
    """
    client = get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        query_embedding = get_embedding(query_text)
        search_query = {
            "size": top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": top_k,
                    }
                }
            },
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }

        response = client.search(index=index_name, body=search_query)
        return response["hits"]["hits"]
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []


def hybrid_search(query_text, top_k=20):
    """
    Perform hybrid search using both keyword and semantic search.

    Args:
        query_text (str): The query text to search for
        top_k (int): Number of results to return

    Returns:
        list: Search results
    """
    client = get_opensearch_client("localhost", 9200)
    index_name = "patents"

    try:
        query_embedding = get_embedding(query_text)
        search_query = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {"knn": {"embedding": {"vector": query_embedding, "k": top_k}}},
                        {"match": {"abstract": query_text}},
                    ]
                }
            },
            "_source": ["title", "abstract", "publication_date", "patent_id"],
        }

        response = client.search(index=index_name, body=search_query)
        return response["hits"]["hits"]
    except Exception as e:
        print(f"Hybrid search error: {e}")
        try:
            fallback_query = {
                "size": top_k,
                "query": {"match": {"abstract": query_text}},
                "_source": ["title", "abstract", "publication_date", "patent_id"],
            }
            response = client.search(index=index_name, body=fallback_query)
            return response["hits"]["hits"]
        except Exception as e2:
            print(f"Fallback search error: {e2}")
            return []


def iterative_search(query_text, refinement_steps=3, top_k=20):
    """
    Perform iterative search with query refinement.

    Args:
        query_text (str): The initial query text
        refinement_steps (int): Number of search refinement iterations
        top_k (int): Number of results per iteration

    Returns:
        list: Search results
    """
    client = get_opensearch_client("localhost", 9200)
    index_name = "patents"

    all_results = []
    current_query = query_text

    for i in range(refinement_steps):
        try:
            search_query = {
                "size": top_k,
                "query": {"match": {"abstract": current_query}},
                "_source": ["title", "abstract", "publication_date", "patent_id"],
            }

            response = client.search(index=index_name, body=search_query)
            results = response["hits"]["hits"]
            for result in results:
                if result not in all_results:
                    all_results.append(result)

            if not results:
                break
                
            if results:
                top_result = results[0]
                current_query = f"{current_query} {top_result['_source']['title']}"

        except Exception as e:
            print(f"Iterative search error at step {i}: {e}")
            break

    return all_results


if __name__ == "__main__":
    query = "lithium battery"
# Currently all commented, you can check each type of search by uncommenting and running each search
    # print("Keyword Search Results:")
    # keyword_results = keyword_search(query)
    # for res in keyword_results:
    #     print(f"Title: {res['_source']['title']}, Patent ID: {res['_source']['patent_id']}")
    #     print(res, end="\n\n")

    # print("\nSemantic Search Results:")
    # semantic_results = semantic_search(query)
    # for res in semantic_results:
    #     # print(f"Title: {res['_source']['title']}, Patent ID: {res['_source']['patent_id']}")
    #     print(res, end="\n\n")

    # print("\nHybrid Search Results:")
    # hybrid_results = hybrid_search(query)
    # for res in hybrid_results:
    #     # print(f"Title: {res['_source']['title']}, Patent ID: {res['_source']['patent_id']}")
    #     print(res, end="\n\n")
