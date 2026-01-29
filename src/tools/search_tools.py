from langchain_tavily import TavilySearch


class SearchTool:
    def __init__(
        self,
        max_results=3,
        search_depth="basic",
        include_raw_content=False,
        include_images=False,
    ):
        self.search_tool = TavilySearch(
            max_results=max_results,
            search_depth=search_depth,
            include_raw_content=include_raw_content,
            include_images=include_images,
        )

    def get_search_tool(self) -> TavilySearch:
        return self.search_tool


obj = SearchTool()
tavily_tool = obj.get_search_tool()
