# app/channels/presence_channel.rb
# Real-time presence tracking for rooms/documents
#
# Usage:
#   # In JavaScript
#   consumer.subscriptions.create(
#     { channel: "PresenceChannel", room_id: roomId },
#     {
#       connected() { this.startHeartbeat() },
#       disconnected() { this.stopHeartbeat() },
#       received(data) { updatePresenceUI(data.users) },
#       startHeartbeat() {
#         this.heartbeatInterval = setInterval(() => this.perform("heartbeat"), 25000)
#       },
#       stopHeartbeat() {
#         clearInterval(this.heartbeatInterval)
#       }
#     }
#   )
#
#   # In view
#   <%= turbo_stream_from @room %>
#   <div id="online_users"></div>
#
# Prerequisites:
#   - Room model (or any scopeable model)
#   - Redis (for production) or Rails.cache (for development)
#   - ApplicationCable::Connection with current_user

class PresenceChannel < ApplicationCable::Channel
  PRESENCE_TIMEOUT = 2.minutes
  COLORS = %w[#ef4444 #f97316 #eab308 #22c55e #14b8a6 #3b82f6 #8b5cf6 #ec4899].freeze

  def subscribed
    @room = Room.find(params[:room_id])
    stream_for @room

    join_room
    broadcast_presence
  end

  def unsubscribed
    leave_room if @room
    broadcast_presence if @room
  end

  # Client heartbeat to maintain presence
  def heartbeat
    update_presence
  end

  # Update cursor position (for collaborative features)
  def cursor_moved(data)
    PresenceChannel.broadcast_to(@room, {
      type: "cursor",
      user_id: current_user.id,
      user_name: current_user.name,
      user_color: user_color,
      x: data["x"],
      y: data["y"]
    })
  end

  # Typing indicator
  def typing(data)
    PresenceChannel.broadcast_to(@room, {
      type: "typing",
      user_id: current_user.id,
      user_name: current_user.name,
      typing: data["typing"]
    })
  end

  private

  def join_room
    add_to_presence_list
    log_presence_event("joined")
  end

  def leave_room
    remove_from_presence_list
    log_presence_event("left")
  end

  def update_presence
    add_to_presence_list
    cleanup_stale_users
  end

  def add_to_presence_list
    presence_store.zadd(presence_key, Time.current.to_f, current_user.id)
  end

  def remove_from_presence_list
    presence_store.zrem(presence_key, current_user.id)
  end

  def cleanup_stale_users
    cutoff = (Time.current - PRESENCE_TIMEOUT).to_f
    presence_store.zremrangebyscore(presence_key, "-inf", cutoff)
  end

  def online_user_ids
    presence_store.zrangebyscore(
      presence_key,
      (Time.current - PRESENCE_TIMEOUT).to_f,
      "+inf"
    )
  end

  def online_users
    User.where(id: online_user_ids).select(:id, :name, :avatar_url)
  end

  def presence_key
    "presence:room:#{@room.id}"
  end

  def presence_store
    # Use Redis in production, Rails.cache for simplicity
    @presence_store ||= if defined?(Redis) && Rails.env.production?
      Redis.new(url: ENV.fetch("REDIS_URL", "redis://localhost:6379/1"))
    else
      PresenceCache.new
    end
  end

  def broadcast_presence
    users = online_users.map { |u| serialize_user(u) }

    # Via ActionCable (for custom JS handling)
    PresenceChannel.broadcast_to(@room, {
      type: "presence_update",
      users: users,
      count: users.size
    })

    # Via Turbo Stream (for HTML update)
    Turbo::StreamsChannel.broadcast_update_to(
      @room,
      target: "online_users",
      partial: "rooms/online_users",
      locals: { users: online_users }
    )

    Turbo::StreamsChannel.broadcast_update_to(
      @room,
      target: "online_count",
      html: users.size.to_s
    )
  end

  def serialize_user(user)
    {
      id: user.id,
      name: user.name,
      avatar_url: user.avatar_url,
      color: user_color_for(user.id)
    }
  end

  def user_color
    user_color_for(current_user.id)
  end

  def user_color_for(user_id)
    COLORS[user_id % COLORS.length]
  end

  def log_presence_event(action)
    Rails.logger.info("[Presence] User #{current_user.id} #{action} room #{@room.id}")
  end
end

# Simple cache adapter for development (mimics Redis sorted set API)
class PresenceCache
  def initialize
    @data = {}
    @mutex = Mutex.new
  end

  def zadd(key, score, member)
    @mutex.synchronize do
      @data[key] ||= {}
      @data[key][member] = score
    end
  end

  def zrem(key, member)
    @mutex.synchronize do
      @data[key]&.delete(member)
    end
  end

  def zrangebyscore(key, min_score, _max_score)
    @mutex.synchronize do
      return [] unless @data[key]

      min = min_score == "-inf" ? -Float::INFINITY : min_score.to_f

      @data[key]
        .select { |_member, score| score >= min }
        .keys
    end
  end

  def zremrangebyscore(key, min_score, max_score)
    @mutex.synchronize do
      return 0 unless @data[key]

      min = min_score == "-inf" ? -Float::INFINITY : min_score.to_f
      max = max_score == "+inf" ? Float::INFINITY : max_score.to_f

      removed = @data[key].select { |_member, score| score >= min && score <= max }
      removed.keys.each { |member| @data[key].delete(member) }
      removed.size
    end
  end
end
