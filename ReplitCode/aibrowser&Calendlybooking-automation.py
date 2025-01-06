from flask import Flask, request, jsonify
import asyncio
from airtop import AsyncAirtop
from airtop import SessionConfigV1
from airtop.core.api_error import ApiError
from datetime import datetime
from pytz import timezone, utc
from dateutil.parser import isoparse
from dateutil.parser import parse

app = Flask(__name__)

AIRTOP_API_KEY = ""


def normalize_to_iso(date_time):
    """
    Normalize the given date-time string to ISO 8601 format.
    Assumes UTC if the time zone is not explicitly provided.
    """
    try:
        # Parse the date-time string
        parsed_datetime = parse(date_time)

        # If no timezone is provided, assume UTC
        if parsed_datetime.tzinfo is None:
            parsed_datetime = parsed_datetime.replace(tzinfo=utc)

        # Return as ISO 8601 format string
        return parsed_datetime.isoformat()
    except Exception as e:
        raise ValueError(f"Invalid date-time format: {date_time}. Error: {e}")

def adjust_to_est(date_time):
    """
    Adjust the given date-time string to EST.
    """
    # Normalize to ISO 8601 first
    normalized_datetime = normalize_to_iso(date_time)

    # Convert to EST
    est_tz = timezone("US/Eastern")
    parsed_datetime = parse(normalized_datetime)
    est_datetime = parsed_datetime.astimezone(est_tz)

    # Format the adjusted datetime
    return est_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")

@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.json

    # Validate required parameters
    required_fields = ["date_time", "first_name", "last_name", "email", "text"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required parameter: {field}"}), 400

    date_time = data["date_time"]
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]
    text = data["text"]

    try:
        # Adjust date_time to EST
        formatted_datetime = adjust_to_est(date_time)

        # Parse month and date
        est_datetime = datetime.strptime(formatted_datetime, "%Y-%m-%dT%H:%M:%S%z")
        month = est_datetime.strftime("%Y-%m")
        date = est_datetime.strftime("%Y-%m-%d")

        # Start the async Airtop client logic
        result = asyncio.run(handle_airtop(formatted_datetime, first_name, last_name, email, text, month, date))
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


async def handle_airtop(date_time, first_name, last_name, email, text, month, date):
    client = None
    session_id = None
    try:
        # Initialize the Airtop client
        client = AsyncAirtop(api_key=AIRTOP_API_KEY)

        # Create a session configuration
        configuration = SessionConfigV1(timeout_minutes=10)

        # Create a session
        session = await client.sessions.create(configuration=configuration)
        if not session or hasattr(session, "errors") and session.errors:
            raise Exception(f"Failed to create session: {session.errors}")

        session_id = session.data.id if session.data else None

        # Create a browser window
        url = (
            f"https://calendly.com/alozie_igbokwe-arbitrageai/testing/{date_time}"
            f"?month={month}&date={date}&name={first_name}%20{last_name}&email={email}"
        )
        window = await client.windows.create(session_id, url=url)
        if not window.data:
            raise Exception("Failed to create window")

        # Add a wait of 5 secs to allow the page to load
        await asyncio.sleep(5)

        # Get the window ID
        window_id = window.data.window_id

        # First API call: Click the schedule event button
        api_response = await client.windows.click(
            session_id=session_id,
            window_id=window_id,
            element_description="can you click the blue button with the I understand text"
        )
        if hasattr(api_response, "error") and api_response.error:
            raise Exception(f"Failed to click schedule event button: {api_response.error}")
        first_result = api_response.data.model_response

        # New API call: Type text into the input box
        api_response_type = await client.windows.type(
            session_id=session_id,
            window_id=window_id,
            text=text,
            element_description="the white box under Please share anything that will help prepare for our meeting."
        )
        if not api_response_type.data:
            raise Exception("Failed to type text into page element")
        type_result = api_response_type.data.model_response

        # Second API call: Click the I understand button
        api_response_2 = await client.windows.click(
            session_id=session_id,
            window_id=window_id,
            element_description="click the blue schedule event button"
        )
        if hasattr(api_response_2, "error") and api_response_2.error:
            raise Exception(f"Failed to click I understand button: {api_response_2.error}")
        second_result = api_response_2.data.model_response

        return {
            "first_click_result": first_result,
            "text_typing_result": type_result,
            "second_click_result": second_result
        }

    except ApiError as e:
        raise Exception(f"API Error: {e.status_code} - {e.body}")

    finally:
        # Terminate the session
        if client is not None and session_id is not None:
            await client.sessions.terminate(session_id)


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080)
