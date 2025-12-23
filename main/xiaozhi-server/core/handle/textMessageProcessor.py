import json

from core.handle.textMessageHandlerRegistry import TextMessageHandlerRegistry

TAG = __name__


class TextMessageProcessor:
    """Message Handler Main Class"""

    def __init__(self, registry: TextMessageHandlerRegistry):
        self.registry = registry

    async def process_message(self, conn, message: str) -> None:
        """Main entry point for message processing"""
        try:
            # Parsing JSON messages
            msg_json = json.loads(message)

            # Processing JSON messages
            if isinstance(msg_json, dict):
                message_type = msg_json.get("type")

                # Log recording
                conn.logger.bind(tag=TAG).info(f"receive{message_type}information：{message}")

                # Acquire and execute processor
                handler = self.registry.get_handler(message_type)
                if handler:
                    await handler.handle(conn, msg_json)
                else:
                    conn.logger.bind(tag=TAG).error(f"receive unknown type message：{message}")
            # Processing purely digital messages
            elif isinstance(msg_json, int):
                conn.logger.bind(tag=TAG).info(f"receive number message：{message}")
                await conn.websocket.send(message)

        except json.JSONDecodeError:
            # Forwarding non-JSON messages directly
            conn.logger.bind(tag=TAG).error(f"parsing error message：{message}")
            await conn.websocket.send(message)
