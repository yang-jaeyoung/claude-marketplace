# Policy Specs (Pundit)

## Overview
Policy specs test authorization logic using Pundit. Verify that users have correct permissions for actions and scopes.

## When to Use
- Testing authorization rules
- Verifying role-based access control
- Testing resource ownership checks
- Testing policy scopes

## Quick Start
```ruby
# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  let(:user) { create(:user) }
  let(:post) { create(:post, user: user) }

  subject { described_class }

  permissions :update? do
    it 'grants access to owner' do
      expect(subject).to permit(user, post)
    end

    it 'denies access to other users' do
      other_user = create(:user)
      expect(subject).not_to permit(other_user, post)
    end
  end
end
```

## Main Patterns

### Pattern 1: Testing Permissions with RSpec Pundit Matchers
```ruby
# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  subject { described_class }

  let(:user) { create(:user) }
  let(:admin) { create(:user, :admin) }
  let(:post) { create(:post, user: user) }

  permissions :show? do
    context 'published post' do
      let(:post) { create(:post, :published) }

      it 'permits anyone' do
        expect(subject).to permit(nil, post)  # Guest
        expect(subject).to permit(user, post)
        expect(subject).to permit(admin, post)
      end
    end

    context 'draft post' do
      let(:post) { create(:post, published: false, user: user) }

      it 'denies guest' do
        expect(subject).not_to permit(nil, post)
      end

      it 'permits owner' do
        expect(subject).to permit(user, post)
      end

      it 'permits admin' do
        expect(subject).to permit(admin, post)
      end

      it 'denies other users' do
        other_user = create(:user)
        expect(subject).not_to permit(other_user, post)
      end
    end
  end

  permissions :create? do
    it 'denies guest' do
      expect(subject).not_to permit(nil, Post.new)
    end

    it 'permits authenticated user' do
      expect(subject).to permit(user, Post.new)
    end
  end

  permissions :update?, :destroy? do
    it 'denies guest' do
      expect(subject).not_to permit(nil, post)
    end

    it 'denies other users' do
      other_user = create(:user)
      expect(subject).not_to permit(other_user, post)
    end

    it 'permits owner' do
      expect(subject).to permit(user, post)
    end

    it 'permits admin' do
      expect(subject).to permit(admin, post)
    end
  end
end
```

### Pattern 2: Testing Policy Scopes
```ruby
# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  let(:user) { create(:user) }
  let(:admin) { create(:user, :admin) }

  describe 'Scope' do
    let!(:published_post) { create(:post, :published) }
    let!(:user_draft) { create(:post, user: user, published: false) }
    let!(:other_draft) { create(:post, published: false) }

    context 'for guest' do
      it 'returns only published posts' do
        scope = Pundit.policy_scope(nil, Post)

        expect(scope).to include(published_post)
        expect(scope).not_to include(user_draft, other_draft)
      end
    end

    context 'for authenticated user' do
      it 'returns published posts and own drafts' do
        scope = Pundit.policy_scope(user, Post)

        expect(scope).to include(published_post, user_draft)
        expect(scope).not_to include(other_draft)
      end
    end

    context 'for admin' do
      it 'returns all posts' do
        scope = Pundit.policy_scope(admin, Post)

        expect(scope).to include(published_post, user_draft, other_draft)
      end
    end
  end
end
```

### Pattern 3: Testing Role-Based Permissions
```ruby
# spec/policies/admin/user_policy_spec.rb
require 'rails_helper'

RSpec.describe Admin::UserPolicy, type: :policy do
  subject { described_class }

  let(:regular_user) { create(:user) }
  let(:moderator) { create(:user, :moderator) }
  let(:admin) { create(:user, :admin) }
  let(:target_user) { create(:user) }

  permissions :index?, :show? do
    it 'denies regular user' do
      expect(subject).not_to permit(regular_user, User)
    end

    it 'permits moderator' do
      expect(subject).to permit(moderator, User)
    end

    it 'permits admin' do
      expect(subject).to permit(admin, User)
    end
  end

  permissions :create?, :update? do
    it 'denies moderator' do
      expect(subject).not_to permit(moderator, target_user)
    end

    it 'permits admin' do
      expect(subject).to permit(admin, target_user)
    end
  end

  permissions :destroy? do
    it 'denies self-deletion' do
      expect(subject).not_to permit(admin, admin)
    end

    it 'permits admin to delete others' do
      expect(subject).to permit(admin, target_user)
    end

    it 'denies moderator' do
      expect(subject).not_to permit(moderator, target_user)
    end
  end
end
```

### Pattern 4: Testing Conditional Permissions
```ruby
# spec/policies/comment_policy_spec.rb
require 'rails_helper'

RSpec.describe CommentPolicy, type: :policy do
  subject { described_class }

  let(:user) { create(:user) }
  let(:comment) { create(:comment, user: user) }

  permissions :update? do
    context 'within edit window (5 minutes)' do
      let(:comment) { create(:comment, user: user, created_at: 2.minutes.ago) }

      it 'permits owner' do
        expect(subject).to permit(user, comment)
      end
    end

    context 'after edit window' do
      let(:comment) { create(:comment, user: user, created_at: 10.minutes.ago) }

      it 'denies owner' do
        expect(subject).not_to permit(user, comment)
      end
    end

    context 'with replies' do
      let(:comment) { create(:comment, user: user) }

      before { create(:comment, parent: comment) }

      it 'denies editing comment with replies' do
        expect(subject).not_to permit(user, comment)
      end
    end
  end

  permissions :destroy? do
    context 'with no replies' do
      it 'permits owner' do
        expect(subject).to permit(user, comment)
      end
    end

    context 'with replies' do
      before { create(:comment, parent: comment) }

      it 'denies deletion' do
        expect(subject).not_to permit(user, comment)
      end

      it 'permits admin' do
        admin = create(:user, :admin)
        expect(subject).to permit(admin, comment)
      end
    end
  end
end
```

### Pattern 5: Testing Organization/Team Permissions
```ruby
# spec/policies/project_policy_spec.rb
require 'rails_helper'

RSpec.describe ProjectPolicy, type: :policy do
  subject { described_class }

  let(:organization) { create(:organization) }
  let(:project) { create(:project, organization: organization) }

  let(:owner) { create(:user) }
  let(:member) { create(:user) }
  let(:outsider) { create(:user) }

  before do
    create(:membership, organization: organization, user: owner, role: :owner)
    create(:membership, organization: organization, user: member, role: :member)
  end

  permissions :show? do
    it 'permits organization members' do
      expect(subject).to permit(owner, project)
      expect(subject).to permit(member, project)
    end

    it 'denies outsiders' do
      expect(subject).not_to permit(outsider, project)
    end
  end

  permissions :update?, :destroy? do
    it 'permits organization owner' do
      expect(subject).to permit(owner, project)
    end

    it 'denies organization member' do
      expect(subject).not_to permit(member, project)
    end

    it 'denies outsider' do
      expect(subject).not_to permit(outsider, project)
    end
  end

  describe 'Scope' do
    let!(:org1_project) { create(:project, organization: organization) }
    let!(:org2_project) { create(:project) }

    it 'returns projects from user organizations' do
      scope = Pundit.policy_scope(member, Project)

      expect(scope).to include(org1_project)
      expect(scope).not_to include(org2_project)
    end
  end
end
```

### Pattern 6: Testing Shared Policies (Inheritance)
```ruby
# app/policies/application_policy.rb
class ApplicationPolicy
  def initialize(user, record)
    @user = user
    @record = record
  end

  def admin?
    user&.admin?
  end

  def owner?
    record.user_id == user&.id
  end

  private

  attr_reader :user, :record
end

# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  def update?
    admin? || owner?
  end
end

# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  subject { described_class }

  let(:user) { create(:user) }
  let(:admin) { create(:user, :admin) }
  let(:post) { create(:post, user: user) }

  permissions :update? do
    it 'permits owner (via owner? from ApplicationPolicy)' do
      expect(subject).to permit(user, post)
    end

    it 'permits admin (via admin? from ApplicationPolicy)' do
      expect(subject).to permit(admin, post)
    end

    it 'denies other users' do
      other_user = create(:user)
      expect(subject).not_to permit(other_user, post)
    end
  end
end
```

### Pattern 7: Testing Headless Policies (No Record)
```ruby
# app/policies/dashboard_policy.rb
class DashboardPolicy < Struct.new(:user, :dashboard)
  def show?
    user.present?
  end

  def admin?
    user&.admin?
  end
end

# spec/policies/dashboard_policy_spec.rb
require 'rails_helper'

RSpec.describe DashboardPolicy, type: :policy do
  subject { described_class }

  permissions :show? do
    it 'denies guest' do
      expect(subject).not_to permit(nil, :dashboard)
    end

    it 'permits authenticated user' do
      user = create(:user)
      expect(subject).to permit(user, :dashboard)
    end
  end

  permissions :admin? do
    it 'denies regular user' do
      user = create(:user)
      expect(subject).not_to permit(user, :dashboard)
    end

    it 'permits admin' do
      admin = create(:user, :admin)
      expect(subject).to permit(admin, :dashboard)
    end
  end
end
```

### Pattern 8: Testing Permitted Attributes
```ruby
# app/policies/post_policy.rb
class PostPolicy < ApplicationPolicy
  def permitted_attributes
    if user&.admin?
      [:title, :body, :published, :featured]
    else
      [:title, :body]
    end
  end
end

# spec/policies/post_policy_spec.rb
require 'rails_helper'

RSpec.describe PostPolicy, type: :policy do
  let(:user) { create(:user) }
  let(:admin) { create(:user, :admin) }
  let(:post) { create(:post) }

  describe '#permitted_attributes' do
    it 'returns limited attributes for regular user' do
      policy = described_class.new(user, post)

      expect(policy.permitted_attributes).to eq([:title, :body])
    end

    it 'returns all attributes for admin' do
      policy = described_class.new(admin, post)

      expect(policy.permitted_attributes).to eq([:title, :body, :published, :featured])
    end
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Testing controller authorization | Wrong layer | Test policies in isolation, integration in request specs |
| Not testing all roles | Security holes | Test guest, user, owner, admin for each action |
| Hardcoding user IDs | Brittle tests | Use factories and associations |
| Not testing scopes | Data leaks | Always test policy scopes |
| Fat policies | Hard to test | Extract complex logic to service objects |

## Related Skills
- [Request Specs](./requests.md): Testing authorization in controllers
- [Models](./models.md): Testing user roles and associations
- [Shared Examples](../patterns/shared-examples.md): DRY policy tests

## References
- [Pundit Documentation](https://github.com/varvet/pundit)
- [RSpec Pundit Matchers](https://github.com/pundit-community/pundit-matchers)
- [Testing Policies](https://github.com/varvet/pundit#testing)
