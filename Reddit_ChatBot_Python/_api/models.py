from typing import Dict, Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Json


class CustomType(str, Enum):
    group = 'group'
    direct = 'direct'


class MemberState(str, Enum):
    joined = 'joined'
    invited = 'invited'


class _Channel(BaseModel):
    name: str
    member_count: int
    custom_type: CustomType
    channel_url: str
    created_at: int
    # cover_url: str
    max_length_message: int
    data: Union[Json, str]

    class Config:
        allow_mutation = False


class User(BaseModel):
    is_blocking_me: Optional[bool]
    user_id: Optional[str]
    is_muted: Optional[bool]
    friend_name: Optional[str]
    joined_ts: Optional[int]
    is_active: Optional[bool]
    read_ts: Optional[int]
    is_blocked_by_me: Optional[bool]
    state: Optional[str]
    # friend_discovery_key: null
    role: Optional[str]
    is_online: Optional[bool]
    require_auth_for_profile_image: Optional[bool]
    # last_seen_at: int
    nickname: Optional[str]
    # profile_url:str
    # metadata: dict

    class Config:
        allow_mutation = False


class Members(BaseModel):
    members: List[User]
    next: str

    class Config:
        allow_mutation = False

    @classmethod
    def _from_dict(cls, d):
        return cls(**d)


class BannedUser(BaseModel):
    description: str
    start_at: int
    user: User
    end_at: int

    class Config:
        allow_mutation = False


class BannedUsers(BaseModel):
    banned_list: List[BannedUser]
    next: str

    class Config:
        allow_mutation = False

    @classmethod
    def _from_dict(cls, d):
        return cls(**d)


class Message(BaseModel):
    # message_survival_seconds: int
    # custom_type: str
    mentioned_users: List[User]
    # translations: dict
    updated_at: Optional[int]
    is_op_msg: Optional[bool]
    is_removed: Optional[bool]
    user: Optional[User]
    # file: dict
    message: str
    data: Union[Json, str]
    # message_retention_hour: int
    # silent: bool
    type: Optional[str]
    created_at: Optional[int]
    req_id: Optional[str]
    mention_type: Optional[str]
    channel_url: str
    message_id: Optional[int]

    class Config:
        allow_mutation = False

    @classmethod
    def _from_dict(cls, d):
        return cls(**d)


class Channel(BaseModel):
    invited_at: Optional[int]
    custom_type: CustomType
    # is_ephemeral: bool
    read_receipt: Dict[str, int]
    member_state: MemberState
    freeze: Optional[bool]
    created_by: Optional[User]
    is_hidden: Optional[bool]
    # disappearing_message: dict
    is_push_enabled: Optional[bool]
    joined_ts: Optional[int]
    is_created: Optional[bool]
    member_count: Optional[int]
    # my_role: str
    # is_broadcast: bool
    last_message: Optional[Message]
    user_last_read: Optional[int]
    unread_mention_count: Optional[int]
    # sms_fallback: dict
    # is_discoverable: bool
    # ignore_profanity_filter: bool
    channel_url: str
    # operators: list
    channel: _Channel
    # message_survival_seconds: int
    unread_message_count: Optional[int]
    # is_distinct: bool
    # is_muted: bool
    # hidden_state: str
    cover_url: Optional[str]
    members: List[User]
    is_public: Optional[bool]
    # data: Union[Json, str]
    # ts_message_offset: int
    joined_member_count: Optional[int]
    is_super: Optional[bool]
    name: Optional[str]
    created_at: Optional[int]
    # is_access_code_required: bool
    # push_trigger_option: str
    max_length_message: Optional[int]
    inviter: Optional[User]
    count_preference: Optional[str]

    class Config:
        allow_mutation = False

    @classmethod
    def _from_dict(cls, d):
        return cls(**d)
