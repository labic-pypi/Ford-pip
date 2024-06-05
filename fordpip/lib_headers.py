#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains recent dataset headers from
FacebookFeeds, Netvizz and Twitter flashback scripts,
used both for mining and parsing operations.
'''

FACEBOOK_POSTS_HEADER = ['id', 'text', 'post_type', 'from_page_id', 'from_name', 'page_type', 'post_date',
    'post_published_unix', 'is_user_post', 'mentions', 'num_likes', 'num_comments', 'num_shares', 'engagement',
    'angry', 'haha', 'love', 'sad', 'thankful', 'wow', 'link']

FACEBOOK_COMMENTS_HEADER = ['comment_id', 'comment_by', 'comment_by_userid', 'comment_message', 'comment_like_count',
    'comment_reply_count', 'comment_length', 'comment_published', 'comment_time', 'post_by', 'post_id',
    'post_text', 'post_date', 'post_published_unix', 'link']

FF_ADVANCED_HEADER = ['ObjectId', 'IdPost', 'Facebook Page', 'TipoColeta', 'TipoDado', 'idPage', 'NomePage',
    'From', 'To', 'WithTags', 'Icon', 'Icon Real', 'Place', 'Targeting', 'Message', 'Picture', 'Picture Real',
    'Full Picture', 'Link', 'Link Real', 'Name', 'Caption', 'Description', 'Type', 'SharesCount', 'Likes',
    'Num_Likes', 'StatusType', 'Story', 'StoryTags', 'Comments', 'Num_Comments', 'Source', 'Source Real',
    'MessageTags', 'Privacy', 'Properties', 'CaptureTime', 'ScheduledPublishTime', 'ScheduledPublishTime_utc',
    'UpdateTime', 'UpdateTime_utc', 'CreatedTime', 'CreatedTime_utc']

FF_BASIC_HEADER = ['IdPost', 'NomePage', 'From.Name', 'Message', 'Link Real', 'Facebook Page',
	'CreatedTime', 'CreatedTime_utc']

FF_CLASSIC_HEADER = ['IdPost', 'TipoColeta', 'TipoDado', 'idPage', 'NomePage', 'From.Name', 'To',
    'Message', 'Picture', 'Link', 'Name', 'Caption', 'Description', 'Type', 'SharesCount',
    'Likes', 'Num_Likes', 'Place', 'StatusType', 'Story', 'StoryTags', 'Comments',
    'Num_Comments', 'CreatedTime', 'CreatedTime_utc']

FF_REACTIONS_HEADER = ['IdPost', 'NomePage', 'From.Name', 'Message', 'Face_Page', 'Num_Likes',
    'Num_Comments', 'Num_Shares', 'ANGRY', 'HAHA', 'LIKE', 'LOVE', 'NONE', 'SAD',
    'THANKFUL', 'WOW', 'CreatedTime', 'CreatedTime_utc']

NETVIZZ_POSTS_HEADER = ['type', 'by', 'post_id', 'post_link', 'post_message', 'picture', 'full_picture',
    'link', 'link_domain', 'post_published', 'post_published_unix', 'post_published_sql', 'likes_count_fb',
    'comments_count_fb', 'reactions_count_fb', 'shares_count_fb', 'engagement_fb',
    # 'comments_retrieved', 'comments_base', 'comments_replies', 'comment_likes_count',
    'rea_LOVE', 'rea_WOW', 'rea_HAHA', 'rea_SAD', 'rea_ANGRY', 'rea_THANKFUL']

NETVIZZ_UK_HEADER = ['status_id', 'status_message', 'link_name', 'status_type', 'status_link',
    'permalink_url', 'status_published', 'num_reactions', 'num_comments', 'num_shares',
    'num_likes', 'num_loves', 'num_wows', 'num_hahas', 'num_sads', 'num_angrys'] # 'UE', 'A.U.E.', 'A.L.', 'A.R.', 'A.C.', 'A.S.'

NETVIZZ_COMMENTS_HEADER = ['post_id', 'post_by', 'post_text', 'post_published', 'comment_id', 'comment_by',
    'is_reply', 'comment_message', 'comment_published', 'comment_like_count']

TWEETS_HEADER = ['text', 'reply_to_user_id', 'from_user', 'id', 'from_user_id', 'lang', 'source', 'user_image_url',
    'geo_type', 'latitude', 'longitude', 'created_at', 'time', 'type', 'rt_count', 'favorite_count', 'place',
    'country', 'country_code', 'hashtags', 'urls', 'media_expanded_url', 'media_url', 'bounding_box', 'mentions_user',
    'mentions_user_id', 'reply_to_user', 'reply_to_id', 'rt_text', 'rt_user_id', 'rt_user', 'rt_id', 'rt_source',
    'rt_created_at', 'quoted_text', 'quoted_id', 'quoted_user', 'quoted_user_id', 'quoted_created_at', 'quoted_source',
    'user_full_name', 'user_tweets', 'user_followers', 'user_following', 'user_listed', 'user_favorited',
    'user_created_at', 'user_lang', 'user_location', 'user_time_zone', 'user_description', 'user_url',
    'user_protected_tweets', 'user_default_layout', 'user_default_image', 'user_verified', 'link']

TWEETS_EC_HEADER = ['lineid', '', 'name', 'username', 'tweet_id_(click_to_view_url)', 'retweets', 'comments', 'favorites',
                    'is_retweet?', 'date', 'tweet_text', 'author_followers', 'author_friends', 'author_favorites',
                    'author_statuses', 'author_bio', 'author_image', 'author_location', 'author_verified', 'tweet_source', 'status_url']

TIKTOK_EC_HEADER = ['lineid', '', 'video_id', 'name_(click_to_view_profile)', 'unique_id', 'date', 'description',
                    'digg_count', 'share_count', 'play_count', 'comment_count', 'music', 'author_following_count',
                    'author_follower_count', 'author_heart_count', 'author_video_count', 'author_digg_count',
                    'video_link', 'author_url', 'video_url']

TIKTOK_USERS_HEADER = ['username', 'name', 'followers', 'following', 'hearts', 'videos', 'diggs', 'url']

TWITTER_USERS_HEADER = ['from_user', 'from_user_id', 'user_image_url', 'user_full_name', 'user_tweets', 'user_followers',
    'user_following', 'user_listed', 'user_favorited', 'user_created_at', 'user_lang', 'user_location', 'user_time_zone',
    'user_description', 'user_url', 'user_protected_tweets', 'user_default_layout', 'user_default_image', 'user_verified']

YTK_HEADER = ['text', 'id', 'from_user', 'created_at', 'time']