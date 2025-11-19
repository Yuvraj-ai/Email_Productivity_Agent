from pydantic import BaseModel, Field
from typing import List, Optional


class Email(BaseModel):
    id : str  =Field(..., description="Unique ID of the email")
    message_id: str = Field(...,description="the unique message id present in the json")
    sender: str = Field(...,description="Email of the sender")
    sender_name: str = Field(...,description="Name of the sender")
    recipients: List = Field(...,description="Emails to which this message has also been sent")
    subject : str = Field(...,description="Subject of the email")
    body: str = Field(...,description="The main content of the email.")
    timestamp : str = Field(..., description="Date and time of when this email was sent.")
    category: Optional[str] = Field(None, description="Category of the email.")
    priority: Optional[str] = Field(None,description="The priority / importance of the email.")
    is_spam: Optional[bool] = Field(False,description="Is the email a spam or not.") 
    action_items: Optional[str] = Field(None,description="Any actions / tasks to be taken by the user given in the email.")
    summary : Optional[str] = Field(...,description="A short summary of the email.")
    has_attachment: Optional[bool] = Field(False,description="Does the email contain any attachment.")
    attachment_names: Optional[List[str]] = Field(None,description="The names of the attachments in the email.")