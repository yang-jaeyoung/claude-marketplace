# spec/factories/posts.rb

FactoryBot.define do
  factory :post do
    user
    title { Faker::Lorem.sentence(word_count: 5) }
    body { Faker::Lorem.paragraphs(number: 3).join("\n\n") }
    published { false }

    trait :published do
      published { true }
      published_at { Time.current }
    end

    trait :draft do
      published { false }
    end

    trait :featured do
      featured { true }
      published { true }
    end

    trait :with_comments do
      transient do
        comments_count { 5 }
      end

      after(:create) do |post, evaluator|
        create_list(:comment, evaluator.comments_count, post: post)
      end
    end

    trait :with_tags do
      transient do
        tags_count { 3 }
      end

      after(:create) do |post, evaluator|
        tags = create_list(:tag, evaluator.tags_count)
        post.tags = tags
      end
    end
  end
end
