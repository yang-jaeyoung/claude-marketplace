# app/forms/application_form.rb
# 복잡한 폼 로직을 캡슐화하는 폼 객체 기본 클래스
#
# 사용법:
#   class RegistrationForm < ApplicationForm
#     attribute :email, :string
#     attribute :password, :string
#     attribute :terms_accepted, :boolean
#
#     validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
#     validates :password, presence: true, length: { minimum: 8 }
#     validates :terms_accepted, acceptance: true
#
#     def save
#       return false unless valid?
#       User.create!(email: email, password: password)
#     end
#   end

class ApplicationForm
  include ActiveModel::Model
  include ActiveModel::Attributes

  def persisted?
    false
  end

  def save
    raise NotImplementedError, "#{self.class}#save must be implemented"
  end

  def save!
    save || raise(ActiveRecord::RecordInvalid, self)
  end
end
