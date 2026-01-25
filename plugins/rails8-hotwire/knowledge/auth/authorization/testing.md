# Testing Authorization Policies

## Overview

Comprehensive guide to testing Pundit policies using RSpec. Covers policy specs, scope testing, permit/forbid matchers, and integration testing.

## When to Use

- When writing specs for new policies
- When verifying authorization rules
- When testing role-based access
- When ensuring security requirements are met

## Quick Start

```ruby
# Gemfile (test group)
gem "pundit-matchers"
```

```ruby
# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  let(:user) { create(:user) }
  let(:admin) { create(:user, :admin) }
  let(:post) { create(:post) }

  subject { described_class }

  permissions :update?, :destroy? do
    it { is_expected.to permit(admin, post) }
    it { is_expected.not_to permit(user, post) }
  end
end
```

## Main Patterns

### Pattern 1: Basic Policy Spec Setup

```ruby
# spec/rails_helper.rb
require 'pundit/rspec'
# or require 'pundit/matchers' for pundit-matchers gem

RSpec.configure do |config|
  config.include Pundit::RSpec::PolicyExampleGroup, type: :policy
end
```

```ruby
# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  subject { described_class.new(user, post) }

  let(:post) { create(:post, user: owner) }
  let(:owner) { create(:user) }

  context "for a visitor" do
    let(:user) { nil }

    it { is_expected.to permit_action(:show) }
    it { is_expected.to forbid_action(:create) }
    it { is_expected.to forbid_action(:update) }
    it { is_expected.to forbid_action(:destroy) }
  end

  context "for a regular user" do
    let(:user) { create(:user) }

    it { is_expected.to permit_action(:show) }
    it { is_expected.to permit_action(:create) }
    it { is_expected.to forbid_action(:update) }
    it { is_expected.to forbid_action(:destroy) }
  end

  context "for the owner" do
    let(:user) { owner }

    it { is_expected.to permit_actions([:show, :create, :update, :destroy]) }
  end

  context "for an admin" do
    let(:user) { create(:user, :admin) }

    it { is_expected.to permit_all_actions }
  end
end
```

### Pattern 2: Using permissions Block (Pundit Built-in)

```ruby
# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  subject { described_class }

  let(:user) { create(:user) }
  let(:admin) { create(:user, :admin) }
  let(:owner) { create(:user) }
  let(:post) { create(:post, user: owner) }

  permissions :show? do
    it "allows anyone to view published posts" do
      post.update(published: true)
      expect(subject).to permit(nil, post)
      expect(subject).to permit(user, post)
    end

    it "denies visitors from viewing drafts" do
      post.update(published: false)
      expect(subject).not_to permit(nil, post)
    end

    it "allows owner to view own drafts" do
      post.update(published: false)
      expect(subject).to permit(owner, post)
    end
  end

  permissions :create? do
    it "allows logged in users" do
      expect(subject).to permit(user, Post)
    end

    it "denies visitors" do
      expect(subject).not_to permit(nil, Post)
    end
  end

  permissions :update?, :destroy? do
    it "allows admin" do
      expect(subject).to permit(admin, post)
    end

    it "allows owner" do
      expect(subject).to permit(owner, post)
    end

    it "denies other users" do
      expect(subject).not_to permit(user, post)
    end

    it "denies visitors" do
      expect(subject).not_to permit(nil, post)
    end
  end

  permissions :publish? do
    it "allows only admins" do
      expect(subject).to permit(admin, post)
      expect(subject).not_to permit(owner, post)
      expect(subject).not_to permit(user, post)
    end
  end
end
```

### Pattern 3: Testing Scopes

```ruby
# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy::Scope, type: :policy do
  subject { described_class.new(user, Post).resolve }

  let!(:published_post) { create(:post, :published) }
  let!(:draft_post) { create(:post, :draft) }
  let!(:user_draft) { create(:post, :draft, user: owner) }
  let(:owner) { create(:user) }

  context "for a visitor" do
    let(:user) { nil }

    it "returns only published posts" do
      expect(subject).to contain_exactly(published_post)
    end
  end

  context "for a regular user" do
    let(:user) { create(:user) }

    it "returns published posts" do
      expect(subject).to include(published_post)
    end

    it "excludes other users' drafts" do
      expect(subject).not_to include(draft_post)
    end
  end

  context "for the owner" do
    let(:user) { owner }

    it "returns published posts and own drafts" do
      expect(subject).to contain_exactly(published_post, user_draft)
    end
  end

  context "for an admin" do
    let(:user) { create(:user, :admin) }

    it "returns all posts" do
      expect(subject).to contain_exactly(published_post, draft_post, user_draft)
    end
  end
end
```

### Pattern 4: Testing Permitted Attributes

```ruby
# spec/policies/user_policy_spec.rb
require 'rails_helper'

RSpec.describe UserPolicy, type: :policy do
  describe "permitted_attributes" do
    subject { described_class.new(user, target_user).permitted_attributes }

    let(:target_user) { create(:user) }

    context "for the user themselves" do
      let(:user) { target_user }

      it "allows profile attributes" do
        expect(subject).to include(:name, :avatar, :bio)
      end

      it "excludes admin attributes" do
        expect(subject).not_to include(:role, :admin)
      end
    end

    context "for an admin" do
      let(:user) { create(:user, :admin) }

      it "allows all attributes including role" do
        expect(subject).to include(:name, :avatar, :bio, :role)
      end
    end
  end
end
```

### Pattern 5: Testing Custom Actions

```ruby
# spec/policies/order_policy_spec.rb
require 'rails_helper'

RSpec.describe OrderPolicy, type: :policy do
  subject { described_class.new(user, order) }

  let(:order) { create(:order, user: customer, status: status) }
  let(:customer) { create(:user) }
  let(:status) { "pending" }

  describe "#cancel?" do
    context "when order is pending" do
      let(:status) { "pending" }

      it "allows customer to cancel" do
        subject = described_class.new(customer, order)
        expect(subject.cancel?).to be true
      end
    end

    context "when order is shipped" do
      let(:status) { "shipped" }

      it "denies customer from cancelling" do
        subject = described_class.new(customer, order)
        expect(subject.cancel?).to be false
      end

      it "allows admin to cancel" do
        admin = create(:user, :admin)
        subject = described_class.new(admin, order)
        expect(subject.cancel?).to be true
      end
    end
  end

  describe "#refund?" do
    let(:status) { "completed" }

    it "allows only admin and staff with refund permission" do
      admin = create(:user, :admin)
      staff = create(:user, :staff)
      customer = create(:user)

      expect(described_class.new(admin, order).refund?).to be true
      expect(described_class.new(staff, order).refund?).to be true
      expect(described_class.new(customer, order).refund?).to be false
    end
  end
end
```

### Pattern 6: Integration Testing with Controllers

```ruby
# spec/requests/posts_spec.rb
require 'rails_helper'

RSpec.describe "Posts", type: :request do
  describe "authorization" do
    let(:user) { create(:user) }
    let(:other_user) { create(:user) }
    let(:post) { create(:post, user: user) }

    describe "PATCH /posts/:id" do
      context "when user owns the post" do
        before { sign_in user }

        it "allows update" do
          patch post_path(post), params: { post: { title: "Updated" } }
          expect(response).to redirect_to(post)
          expect(post.reload.title).to eq("Updated")
        end
      end

      context "when user doesn't own the post" do
        before { sign_in other_user }

        it "denies update" do
          patch post_path(post), params: { post: { title: "Hacked" } }
          expect(response).to redirect_to(root_path)
          expect(post.reload.title).not_to eq("Hacked")
        end
      end

      context "when not signed in" do
        it "redirects to sign in" do
          patch post_path(post), params: { post: { title: "Updated" } }
          expect(response).to redirect_to(new_user_session_path)
        end
      end
    end
  end
end
```

### Pattern 7: Testing Multi-Tenant Policies

```ruby
# spec/policies/project_policy_spec.rb
require 'rails_helper'

RSpec.describe ProjectPolicy, type: :policy do
  subject { described_class.new(user, project) }

  let(:organization) { create(:organization) }
  let(:other_org) { create(:organization) }
  let(:project) { create(:project, organization: organization) }

  context "user from same organization" do
    let(:user) { create(:user, organization: organization) }

    it { is_expected.to permit_action(:show) }
    it { is_expected.to permit_action(:update) }
  end

  context "user from different organization" do
    let(:user) { create(:user, organization: other_org) }

    it { is_expected.to forbid_action(:show) }
    it { is_expected.to forbid_action(:update) }
    it { is_expected.to forbid_action(:destroy) }
  end

  describe "scope" do
    let!(:org_project) { create(:project, organization: organization) }
    let!(:other_project) { create(:project, organization: other_org) }

    it "returns only same organization projects" do
      user = create(:user, organization: organization)
      scope = described_class::Scope.new(user, Project).resolve

      expect(scope).to include(org_project)
      expect(scope).not_to include(other_project)
    end
  end
end
```

### Pattern 8: Testing Edge Cases

```ruby
# spec/policies/comment_policy_spec.rb
require 'rails_helper'

RSpec.describe CommentPolicy, type: :policy do
  describe "#destroy?" do
    let(:post) { create(:post) }
    let(:comment) { create(:comment, post: post, user: commenter, created_at: created_at) }
    let(:commenter) { create(:user) }
    let(:created_at) { 1.hour.ago }

    context "when comment is recent (within edit window)" do
      let(:created_at) { 10.minutes.ago }

      it "allows commenter to delete" do
        policy = described_class.new(commenter, comment)
        expect(policy.destroy?).to be true
      end
    end

    context "when comment is old (outside edit window)" do
      let(:created_at) { 2.hours.ago }

      it "denies commenter from deleting" do
        policy = described_class.new(commenter, comment)
        expect(policy.destroy?).to be false
      end

      it "still allows admin to delete" do
        admin = create(:user, :admin)
        policy = described_class.new(admin, comment)
        expect(policy.destroy?).to be true
      end

      it "still allows post owner to delete" do
        policy = described_class.new(post.user, comment)
        expect(policy.destroy?).to be true
      end
    end

    context "when post is locked" do
      before { post.update(locked: true) }

      it "denies commenter from deleting even recent comments" do
        comment.update(created_at: 5.minutes.ago)
        policy = described_class.new(commenter, comment)
        expect(policy.destroy?).to be false
      end
    end
  end
end
```

## Pundit Matchers Reference

```ruby
# From pundit-matchers gem
it { is_expected.to permit_action(:show) }
it { is_expected.to forbid_action(:destroy) }
it { is_expected.to permit_actions([:show, :index]) }
it { is_expected.to forbid_actions([:create, :update]) }
it { is_expected.to permit_all_actions }
it { is_expected.to forbid_all_actions }
it { is_expected.to permit_new_and_create_actions }
it { is_expected.to permit_edit_and_update_actions }
```

## Anti-patterns

| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Testing Pundit internals | Unnecessary, already tested | Test your logic only |
| Not testing nil user | Guest access untested | Always test visitor case |
| Only testing happy path | Security holes | Test denied scenarios |
| Large setup blocks | Hard to read | Use let and contexts |

## Related Skills

- [pundit.md](./pundit.md): Pundit setup
- [policies.md](./policies.md): Writing policies
- [scopes.md](./scopes.md): Scope patterns

## References

- [Pundit RSpec](https://github.com/varvet/pundit#rspec)
- [pundit-matchers](https://github.com/pundit-community/pundit-matchers)
