# app/models/concerns/broadcastable.rb
# Enhanced broadcasting concern for models with customizable options
#
# Usage:
#   class Message < ApplicationRecord
#     include Broadcastable
#
#     belongs_to :room
#     belongs_to :user
#
#     # Simple: broadcast to parent
#     broadcasts_to_parent :room
#
#     # Custom: with options
#     broadcasts_changes target: "messages",
#                        inserts_by: :prepend,
#                        partial: "messages/message"
#
#     # Conditional broadcasting
#     broadcasts_to_parent :room, if: :published?
#   end
#
# Prerequisites:
#   - Turbo Rails gem
#   - Parent association for broadcasts_to_parent
#   - Partials matching model name (or custom partial option)

module Broadcastable
  extend ActiveSupport::Concern

  included do
    include Turbo::Broadcastable

    class_attribute :broadcast_config, default: {}
  end

  class_methods do
    # Broadcast to a parent association
    # @param association [Symbol] the parent association name
    # @param options [Hash] broadcasting options
    #   :target - DOM target ID (default: pluralized model name)
    #   :partial - partial path (default: model partial)
    #   :inserts_by - :append or :prepend (default: :append)
    #   :if - condition for broadcasting (Symbol only - method name)
    #   :unless - condition to skip broadcasting (Symbol only - method name)
    def broadcasts_to_parent(association, **options)
      self.broadcast_config = options.merge(association: association)

      after_create_commit :broadcast_created, if: :should_broadcast?
      after_update_commit :broadcast_updated, if: :should_broadcast?
      after_destroy_commit :broadcast_destroyed, if: :should_broadcast?
    end

    # Simplified broadcasts_changes for common patterns
    def broadcasts_changes(**options)
      self.broadcast_config = options

      after_create_commit :broadcast_created_to_stream, if: :should_broadcast?
      after_update_commit :broadcast_updated_to_stream, if: :should_broadcast?
      after_destroy_commit :broadcast_destroyed_from_stream, if: :should_broadcast?
    end
  end

  private

  def should_broadcast?
    config = self.class.broadcast_config

    if_condition = config[:if]
    unless_condition = config[:unless]

    passes_if = if_condition.nil? || check_condition(if_condition)
    passes_unless = unless_condition.nil? || !check_condition(unless_condition)

    passes_if && passes_unless
  end

  def check_condition(condition)
    # Only Symbol conditions are supported for safety
    return true unless condition.is_a?(Symbol)
    send(condition)
  end

  def broadcast_stream
    config = self.class.broadcast_config
    association = config[:association]

    if association
      send(association)
    else
      config[:stream] || self.class.model_name.plural
    end
  end

  def broadcast_target
    config = self.class.broadcast_config
    config[:target] || self.class.model_name.plural
  end

  def broadcast_partial
    config = self.class.broadcast_config
    config[:partial] || to_partial_path
  end

  def broadcast_locals
    { self.class.model_name.singular.to_sym => self }
  end

  def inserts_by
    self.class.broadcast_config[:inserts_by] || :append
  end

  # Callbacks for broadcasts_to_parent

  def broadcast_created
    case inserts_by
    when :prepend
      broadcast_prepend_to(
        broadcast_stream,
        target: broadcast_target,
        partial: broadcast_partial,
        locals: broadcast_locals
      )
    else
      broadcast_append_to(
        broadcast_stream,
        target: broadcast_target,
        partial: broadcast_partial,
        locals: broadcast_locals
      )
    end

    broadcast_counter_update
  end

  def broadcast_updated
    broadcast_replace_to(
      broadcast_stream,
      target: self,
      partial: broadcast_partial,
      locals: broadcast_locals
    )
  end

  def broadcast_destroyed
    broadcast_remove_to(broadcast_stream, target: self)
    broadcast_counter_update
  end

  # Callbacks for broadcasts_changes (custom stream)

  def broadcast_created_to_stream
    stream = self.class.broadcast_config[:stream] || "#{self.class.model_name.plural}_updates"

    case inserts_by
    when :prepend
      Turbo::StreamsChannel.broadcast_prepend_to(
        stream,
        target: broadcast_target,
        partial: broadcast_partial,
        locals: broadcast_locals
      )
    else
      Turbo::StreamsChannel.broadcast_append_to(
        stream,
        target: broadcast_target,
        partial: broadcast_partial,
        locals: broadcast_locals
      )
    end
  end

  def broadcast_updated_to_stream
    stream = self.class.broadcast_config[:stream] || "#{self.class.model_name.plural}_updates"

    Turbo::StreamsChannel.broadcast_replace_to(
      stream,
      target: ActionView::RecordIdentifier.dom_id(self),
      partial: broadcast_partial,
      locals: broadcast_locals
    )
  end

  def broadcast_destroyed_from_stream
    stream = self.class.broadcast_config[:stream] || "#{self.class.model_name.plural}_updates"

    Turbo::StreamsChannel.broadcast_remove_to(
      stream,
      target: ActionView::RecordIdentifier.dom_id(self)
    )
  end

  # Optional counter update

  def broadcast_counter_update
    config = self.class.broadcast_config
    counter_target = config[:counter_target]

    return unless counter_target

    association = config[:association]
    parent = send(association)
    count_method = config[:count_method] || "#{self.class.model_name.plural}_count"
    count = parent.respond_to?(count_method) ? parent.send(count_method) : parent.send(self.class.model_name.plural).count

    broadcast_update_to(
      parent,
      target: counter_target,
      html: count.to_s
    )
  end
end

# Example usage:
#
# class Comment < ApplicationRecord
#   include Broadcastable
#
#   belongs_to :post
#   belongs_to :user
#
#   broadcasts_to_parent :post,
#                        target: "comments",
#                        inserts_by: :prepend,
#                        counter_target: "comments_count",
#                        if: :approved?
# end
#
# class Activity < ApplicationRecord
#   include Broadcastable
#
#   broadcasts_changes stream: "activity_feed",
#                      target: "activities",
#                      inserts_by: :prepend
# end
