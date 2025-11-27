# Backend Setup & Documentation
This is the FastAPI + Strawberry GraphQL backend for the Assignment

## Table of Contents
1. Environment Setup
2. Installation
3. Migration Guide
4. Running the Application
5. GraphQL Schema
   - Queries
   - Mutations
   - Subscriptions

## Environment Setup

### Create Virtual Environment
python3 -m venv venv
# Activate virtual environment (macOS/Linux)
source venv/bin/activate
# Activate virtual environment (Windows)
venv\Scripts\activate
```


### Install Requirements
# Make sure virtual environment is activated
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt


### Environment Configuration
cp .env.example .env
# Key variables needed:
# - MONGODB_URL: MongoDB connection string
# - DATABASE_NAME: Database name
# - BACKEND_URL: Backend base URL (for media file serving)
# - SECRET_KEY: JWT secret key for authentication
# - ALGORITHM: JWT algorithm (default: HS256)

## Migration
### FIles
1. **001_create_users_collection.py** - Creates users collection
2. **002_create_stores_collection.py** - Creates stores collection
3. **003_add_session_tracking.py** - Adds session tracking for stores
4. **004_add_model_move_tracking.py** - Adds model movement tracking
5. **005_create_widget_collections.py** - Creates widget and analytics collections
6. **006_fix_widget_store_ids.py** - Fixes widget store_id mismatch

### How to run Migrations

python manage.py migrate
python migrate_config.py status
python migrate_config.py history
```

### How to create new migration
# Create a new migration file
# Name format: NNN_migration_description.py
# Then run migrations
python manage.py migrate

### Start the Backend Server
source venv/bin/activate
cd app
uvicron main:app --reload
http://localhost:8000

### GraphQL Endpoint
http://localhost:8000/graphql
localhost:8000/graphql

### Access GraphQL Playground
http://localhost:8000/graphql

### Queries
#### User Queries
graphql
  query {
    hello
  }


#### Store Queries
getAllStores
graphql
  query {
    getAllStores {
      id
      name
      description
      imageUrl
      activeUserCount
      models {
        name
        glbUrl
        position
        size
        entranceOrder
      }
      installedWidgetId
      installedWidgetDomain
    }
  }
#### Widget Queries
  graphql
  query {
    getWidgetById(widgetId: "65d1a2b3c4d5e6f7g8h9i0j1") {
      id
      storeId
      domain
      videoUrl
      bannerText
      isActive
      createdAt
      updatedAt
    }
  }

#### Analytics
graphql
  query {
    getAnalyticsSummary(storeId: "6927096be9b2f6e3072031b2") {
      pageView
      videoLoaded
      linkClicked
    }
  }

### Subscriptions
graphql
  subscription {
    storeUpdated(storeId: "6927096be9b2f6e3072031b2") {
      id
      name
      activeUserCount
      models {
        name
        position
      }
      installedWidgetId
    }
  }

## Types
### Store
graphql
type Store {
  id: String!
  name: String!
  description: String!
  imageUrl: String!
  models: [Model!]!
  activeUserCount: Int!
  sessionId: String
  installedWidgetId: String
  installedWidgetDomain: String
}