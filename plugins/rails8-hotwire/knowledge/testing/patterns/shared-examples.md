# Shared Examples and Contexts

## Overview
Shared examples and contexts reduce duplication in tests by extracting common behavior into reusable blocks.

## When to Use
- Testing similar behavior across multiple models/controllers
- DRYing up authorization tests
- Reusing setup code across spec files
- Testing common interfaces (polymorphic behavior)

## Quick Start
```ruby
# spec/support/shared_examples/auditable.rb
RSpec.shared_examples 'auditable' do
  it { should have_many(:audits) }

  it 'creates audit on update' do
    expect {
      subject.update(name: 'New Name')
    }.to change(Audit, :count).by(1)
  end
end

# spec/models/post_spec.rb
RSpec.describe Post, type: :model do
  it_behaves_like 'auditable'
end
```

## Main Patterns

### Pattern 1: Shared Examples with it_behaves_like
```ruby
# spec/support/shared_examples/publishable.rb
RSpec.shared_examples 'publishable' do
  describe '#published?' do
    context 'when published is true' do
      it 'returns true' do
        subject.published = true
        expect(subject).to be_published
      end
    end

    context 'when published is false' do
      it 'returns false' do
        subject.published = false
        expect(subject).not_to be_published
      end
    end
  end

  describe '#publish!' do
    it 'sets published to true' do
      subject.publish!
      expect(subject).to be_published
    end

    it 'sets published_at timestamp' do
      freeze_time do
        subject.publish!
        expect(subject.published_at).to eq(Time.current)
      end
    end
  end
end

# spec/models/post_spec.rb
RSpec.describe Post, type: :model do
  subject { build(:post) }

  it_behaves_like 'publishable'
end

# spec/models/article_spec.rb
RSpec.describe Article, type: :model do
  subject { build(:article) }

  it_behaves_like 'publishable'
end
```

### Pattern 2: Parameterized Shared Examples
```ruby
# spec/support/shared_examples/sortable.rb
RSpec.shared_examples 'sortable' do |factory, sort_field|
  describe ".sorted_by_#{sort_field}" do
    let!(:first) { create(factory, sort_field => 'A') }
    let!(:second) { create(factory, sort_field => 'B') }
    let!(:third) { create(factory, sort_field => 'C') }

    it "sorts by #{sort_field} ascending" do
      result = described_class.send("sorted_by_#{sort_field}", :asc)
      expect(result).to eq([first, second, third])
    end

    it "sorts by #{sort_field} descending" do
      result = described_class.send("sorted_by_#{sort_field}", :desc)
      expect(result).to eq([third, second, first])
    end
  end
end

# spec/models/post_spec.rb
RSpec.describe Post, type: :model do
  it_behaves_like 'sortable', :post, :title
  it_behaves_like 'sortable', :post, :created_at
end

# spec/models/user_spec.rb
RSpec.describe User, type: :model do
  it_behaves_like 'sortable', :user, :name
  it_behaves_like 'sortable', :user, :email
end
```

### Pattern 3: Shared Context for Setup
```ruby
# spec/support/shared_contexts/with_authenticated_user.rb
RSpec.shared_context 'with authenticated user' do
  let(:user) { create(:user) }

  before do
    sign_in user
  end
end

RSpec.shared_context 'with admin user' do
  let(:admin) { create(:user, :admin) }

  before do
    sign_in admin
  end
end

# spec/requests/posts_spec.rb
RSpec.describe 'Posts', type: :request do
  include_context 'with authenticated user'

  describe 'POST /posts' do
    it 'creates a post' do
      post posts_path, params: { post: attributes_for(:post) }
      expect(response).to have_http_status(:redirect)
    end
  end
end

# Automatic inclusion via metadata
RSpec.configure do |config|
  config.include_context 'with authenticated user', :authenticated
  config.include_context 'with admin user', :admin
end

# Usage with metadata
RSpec.describe 'Admin::Posts', type: :request, :admin do
  # admin context automatically included
end
```

### Pattern 4: Shared Examples for Authorization
```ruby
# spec/support/shared_examples/authorizable.rb
RSpec.shared_examples 'requires authentication' do |action, params = {}|
  context 'when not authenticated' do
    it 'redirects to login' do
      send(action, params)
      expect(response).to redirect_to(new_session_path)
    end
  end
end

RSpec.shared_examples 'admin only' do |action, params = {}|
  context 'when authenticated as regular user' do
    before { sign_in create(:user) }

    it 'returns forbidden' do
      send(action, params)
      expect(response).to have_http_status(:forbidden)
    end
  end

  context 'when authenticated as admin' do
    before { sign_in create(:user, :admin) }

    it 'returns success' do
      send(action, params)
      expect(response).to be_successful
    end
  end
end

# spec/requests/admin/users_spec.rb
RSpec.describe 'Admin::Users', type: :request do
  describe 'GET /admin/users' do
    it_behaves_like 'requires authentication', :get, '/admin/users'
    it_behaves_like 'admin only', :get, '/admin/users'
  end

  describe 'DELETE /admin/users/:id' do
    let(:user) { create(:user) }

    it_behaves_like 'requires authentication', :delete, -> { "/admin/users/#{user.id}" }
    it_behaves_like 'admin only', :delete, -> { "/admin/users/#{user.id}" }
  end
end
```

### Pattern 5: Shared Examples for Turbo Responses
```ruby
# spec/support/shared_examples/turbo_stream_response.rb
RSpec.shared_examples 'turbo stream response' do |action_type, target|
  it 'responds with turbo_stream format' do
    expect(response.media_type).to eq('text/vnd.turbo-stream.html')
  end

  it "includes #{action_type} action" do
    expect(response.body).to include("action=\"#{action_type}\"")
  end

  it "targets #{target}" do
    expect(response.body).to include("target=\"#{target}\"")
  end
end

# spec/requests/posts_spec.rb
RSpec.describe 'Posts', type: :request do
  let(:user) { create(:user) }
  let(:headers) { { 'Accept' => 'text/vnd.turbo-stream.html' } }

  before { sign_in user }

  describe 'POST /posts' do
    it 'creates post and responds with turbo stream' do
      post posts_path,
           params: { post: attributes_for(:post) },
           headers: headers

      it_behaves_like 'turbo stream response', 'append', 'posts'
    end
  end

  describe 'DELETE /posts/:id' do
    let!(:post_record) { create(:post, user: user) }

    it 'deletes post and responds with turbo stream' do
      delete post_path(post_record), headers: headers

      it_behaves_like 'turbo stream response', 'remove', dom_id(post_record)
    end
  end
end
```

### Pattern 6: Shared Examples for Validations
```ruby
# spec/support/shared_examples/validations.rb
RSpec.shared_examples 'validates presence of' do |attribute|
  it "requires #{attribute}" do
    subject.send("#{attribute}=", nil)
    expect(subject).not_to be_valid
    expect(subject.errors[attribute]).to include("can't be blank")
  end
end

RSpec.shared_examples 'validates uniqueness of' do |attribute|
  it "requires #{attribute} to be unique" do
    existing = create(described_class.name.underscore.to_sym)
    subject.send("#{attribute}=", existing.send(attribute))
    expect(subject).not_to be_valid
    expect(subject.errors[attribute]).to include("has already been taken")
  end
end

# spec/models/user_spec.rb
RSpec.describe User, type: :model do
  subject { build(:user) }

  it_behaves_like 'validates presence of', :email
  it_behaves_like 'validates presence of', :name
  it_behaves_like 'validates uniqueness of', :email
end
```

### Pattern 7: Shared Examples with Block Parameters
```ruby
# spec/support/shared_examples/api_response.rb
RSpec.shared_examples 'successful JSON response' do |expected_keys = []|
  it 'returns success status' do
    expect(response).to have_http_status(:success)
  end

  it 'returns JSON content type' do
    expect(response.content_type).to match(/application\/json/)
  end

  if expected_keys.any?
    it "includes expected keys: #{expected_keys.join(', ')}" do
      json = JSON.parse(response.body)
      expected_keys.each do |key|
        expect(json).to have_key(key.to_s)
      end
    end
  end
end

RSpec.shared_examples 'error JSON response' do |status, error_message|
  it "returns #{status} status" do
    expect(response).to have_http_status(status)
  end

  it 'includes error message' do
    json = JSON.parse(response.body)
    expect(json['error']).to eq(error_message)
  end
end

# spec/requests/api/posts_spec.rb
RSpec.describe 'API::Posts', type: :request do
  describe 'GET /api/posts' do
    before do
      create_list(:post, 3)
      get api_posts_path
    end

    it_behaves_like 'successful JSON response', [:posts, :meta]
  end

  describe 'POST /api/posts' do
    context 'with invalid params' do
      before do
        post api_posts_path, params: { post: { title: '' } }
      end

      it_behaves_like 'error JSON response', :unprocessable_entity, 'Validation failed'
    end
  end
end
```

### Pattern 8: Nested Shared Examples
```ruby
# spec/support/shared_examples/crud_actions.rb
RSpec.shared_examples 'CRUD actions' do |resource_name|
  let(:factory) { resource_name }
  let(:resource) { create(factory) }

  describe 'GET #index' do
    it 'returns success' do
      get :index
      expect(response).to be_successful
    end
  end

  describe 'GET #show' do
    it 'returns success' do
      get :show, params: { id: resource.id }
      expect(response).to be_successful
    end
  end

  shared_examples 'requires authentication' do
    context 'when not authenticated' do
      it 'redirects to login' do
        get :new
        expect(response).to redirect_to(new_session_path)
      end
    end
  end

  describe 'GET #new' do
    it_behaves_like 'requires authentication'

    context 'when authenticated' do
      before { sign_in create(:user) }

      it 'returns success' do
        get :new
        expect(response).to be_successful
      end
    end
  end
end

# spec/controllers/posts_controller_spec.rb
RSpec.describe PostsController, type: :controller do
  it_behaves_like 'CRUD actions', :post
end
```

### Pattern 9: Shared Examples for Background Jobs
```ruby
# spec/support/shared_examples/enqueueable.rb
RSpec.shared_examples 'enqueues job' do |job_class, with_args: nil, on_queue: nil|
  it "enqueues #{job_class.name}" do
    if with_args
      expect { subject }.to have_enqueued_job(job_class).with(*with_args)
    else
      expect { subject }.to have_enqueued_job(job_class)
    end
  end

  if on_queue
    it "enqueues on #{on_queue} queue" do
      expect { subject }.to have_enqueued_job(job_class).on_queue(on_queue)
    end
  end
end

# spec/models/post_spec.rb
RSpec.describe Post, type: :model do
  describe 'after_create callback' do
    subject { create(:post, :published) }

    it_behaves_like 'enqueues job', PostNotificationJob,
                    with_args: [kind_of(Integer)],
                    on_queue: 'notifications'
  end
end
```

## Anti-patterns
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Overusing shared examples | Hard to understand tests | Use only for truly shared behavior |
| Too many parameters | Complex, hard to read | Break into smaller shared examples |
| Testing different behavior | Confusing test output | Create separate shared examples |
| Not documenting parameters | Hard to use | Add clear comments/docs |
| Shared examples that are too specific | Not reusable | Keep them general |

## Related Skills
- [RSpec Setup](../setup/rspec.md): Configuring shared contexts
- [Models](../types/models.md): Model testing
- [Requests](../types/requests.md): Request testing

## References
- [RSpec Shared Examples](https://rspec.info/features/3-12/rspec-core/example-groups/shared-examples/)
- [Shared Context](https://rspec.info/features/3-12/rspec-core/example-groups/shared-context/)
- [Better Specs - DRY](https://www.betterspecs.org/#shared_examples)
