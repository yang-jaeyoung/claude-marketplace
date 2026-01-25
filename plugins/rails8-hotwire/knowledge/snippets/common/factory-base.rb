# spec/factories/application.rb
# FactoryBot 기본 팩토리 패턴
#
# 사용법:
#   user = create(:user)
#   user = build(:user, name: "Custom")
#   users = create_list(:user, 3)

# === User 팩토리 ===
FactoryBot.define do
  factory :user do
    sequence(:email) { |n| "user#{n}@example.com" }
    name { Faker::Name.name }
    password { "password123" }
    password_confirmation { "password123" }

    # Trait: 관리자
    trait :admin do
      admin { true }
    end

    # Trait: 확인된 이메일
    trait :confirmed do
      confirmed_at { Time.current }
    end

    # 연관 관계 팩토리
    factory :admin_user, traits: [:admin]
    factory :confirmed_user, traits: [:confirmed]
  end
end

# === Account 팩토리 (멀티테넌트) ===
FactoryBot.define do
  factory :account do
    sequence(:name) { |n| "Account #{n}" }
    plan { "free" }

    trait :with_subscription do
      plan { "professional" }
      stripe_customer_id { "cus_#{SecureRandom.hex(8)}" }
      stripe_subscription_id { "sub_#{SecureRandom.hex(8)}" }
      subscription_ends_at { 1.month.from_now }
    end
  end
end

# === Post 팩토리 (일반 모델) ===
FactoryBot.define do
  factory :post do
    association :user
    title { Faker::Lorem.sentence }
    body { Faker::Lorem.paragraphs(number: 3).join("\n\n") }
    published { false }

    trait :published do
      published { true }
      published_at { Time.current }
    end

    trait :with_comments do
      after(:create) do |post|
        create_list(:comment, 3, post: post)
      end
    end
  end
end

# === Comment 팩토리 (중첩 관계) ===
FactoryBot.define do
  factory :comment do
    association :user
    association :post
    body { Faker::Lorem.paragraph }

    trait :threaded do
      association :parent, factory: :comment
    end
  end
end

# === Upload 팩토리 (파일 첨부) ===
FactoryBot.define do
  factory :upload do
    association :user
    status { "pending" }

    trait :with_csv_file do
      after(:build) do |upload|
        upload.file.attach(
          io: File.open(Rails.root.join("spec/fixtures/files/sample.csv")),
          filename: "sample.csv",
          content_type: "text/csv"
        )
      end
    end

    trait :completed do
      status { "completed" }
      completed_at { Time.current }
      results { { created: 10, updated: 5, failed: 0 } }
    end
  end
end
