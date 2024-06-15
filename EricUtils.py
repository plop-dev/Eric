class UserQueryError(Exception):
    pass


def get_song_time_remaining(song_id, sp):
    track = sp.track(song_id)
    progress_ms = track['progress_ms']
    duration_ms = track['duration_ms']
    time_remaining = duration_ms - progress_ms
    return time_remaining
