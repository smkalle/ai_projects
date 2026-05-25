import json

from google.adk.agents.llm_agent import Agent

from .tools import evaluate_infographic, generate_infographic, log_step, scrape_blog


def create_infographic_workflow(url: str) -> str:
    """
    Create an infographic from a blog URL, evaluate it, and regenerate once if needed.
    """
    log_step(f"--- Starting Infographic Workflow for {url} ---")

    summary = scrape_blog(url)
    if summary.startswith("Error"):
        log_step("--- Workflow stopped during scraping ---")
        return summary

    image_path = generate_infographic(summary, attempt=1)
    if image_path.startswith("Error"):
        log_step("--- Workflow stopped during initial generation ---")
        return image_path

    eval_json_str = evaluate_infographic(image_path, summary)
    final_attempt = 1

    try:
        eval_data = json.loads(eval_json_str)
        if not eval_data.get("passed", False):
            log_step("Initial evaluation failed. Attempting regeneration...")
            image_path = generate_infographic(
                summary,
                feedback=eval_data.get("feedback", "Improve factual accuracy, spelling, and visual alignment."),
                attempt=2,
            )
            if image_path.startswith("Error"):
                log_step("--- Workflow stopped during regeneration ---")
                return image_path

            final_attempt = 2
            eval_json_str = evaluate_infographic(image_path, summary)
            eval_data = json.loads(eval_json_str)
            if eval_data.get("passed"):
                log_step("Regeneration successful.")
            else:
                log_step("Regeneration still failed. Finalizing with current version.")
    except Exception as e:
        log_step(f"Critical error parsing evaluation: {str(e)}")

    log_step("--- Workflow Complete ---")
    return (
        "Infographic workflow completed. "
        f"Final image: {image_path}. "
        f"Attempts: {final_attempt}. "
        f"Final evaluation: {eval_json_str}"
    )


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="infographic_agent",
    description="Creates and self-evaluates infographics from blog post URLs.",
    instruction="""You create visual infographics from blog posts.
When the user provides a blog URL, call create_infographic_workflow.
The workflow must scrape the blog, generate an infographic with Nano Banana,
evaluate factual accuracy, spelling, and aesthetic alignment, and regenerate
once with evaluator feedback if the first attempt fails. Report the final image
path, attempt count, and evaluation summary.""",
    tools=[create_infographic_workflow]
)

infographic_agent = root_agent
