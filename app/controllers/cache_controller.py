"""
Cache Controller (Business Logic)
Handles query caching for improved performance
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import QueryCache
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheController:
    """Controller for managing query cache"""

    def __init__(self, db: Session):
        """
        Initialize cache controller.

        Args:
            db: Database session for cache operations.
        """
        self.db = db

    def get_cached_result(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result for a query if available and not expired.

        Updates access statistics when a cache hit occurs.

        Args:
            query_hash: Hash of the query to look up.

        Returns:
            Cached result dictionary with answer, sources, and metadata if found
            and not expired. Returns None if cache is disabled, not found, or expired.
        """
        if not settings.ENABLE_CACHE:
            return None

        try:
            cached = self.db.query(QueryCache).filter(
                QueryCache.query_hash == query_hash,
                QueryCache.expires_at > datetime.utcnow()
            ).first()

            if cached:
                cached.hit_count += 1
                cached.last_accessed = datetime.utcnow()
                self.db.commit()

                logger.info(f"Cache hit for query hash: {query_hash[:8]}...")
                return {
                    "answer": cached.answer,
                    "sources": cached.sources,
                    "metadata": cached.metadata_
                }

            logger.info(f"Cache miss for query hash: {query_hash[:8]}...")
            return None

        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None

    def cache_result(
        self,
        query_hash: str,
        query_text: str,
        answer: str,
        sources: list,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Store a query result in the cache.

        Creates a new cache entry or updates an existing one. Cache entries
        are set to expire based on the configured TTL setting.

        Args:
            query_hash: Hash of the query for quick lookup.
            query_text: Original query text for reference.
            answer: Generated answer to cache.
            sources: List of source references for the answer.
            metadata: Additional metadata about the query or answer.

        Returns:
            True if result was cached successfully, False otherwise.
        """
        if not settings.ENABLE_CACHE:
            return False

        try:
            existing = self.db.query(QueryCache).filter(
                QueryCache.query_hash == query_hash
            ).first()

            expires_at = datetime.utcnow() + timedelta(seconds=settings.CACHE_TTL)

            if existing:
                existing.answer = answer
                existing.sources = sources
                existing.metadata_ = metadata or {}
                existing.expires_at = expires_at
                existing.last_accessed = datetime.utcnow()
            else:
                cache_entry = QueryCache(
                    query_hash=query_hash,
                    query_text=query_text,
                    answer=answer,
                    sources=sources,
                    metadata_=metadata or {},
                    hit_count=0,
                    expires_at=expires_at
                )
                self.db.add(cache_entry)

            self.db.commit()
            logger.info(f"Cached result for query hash: {query_hash[:8]}...")
            return True

        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")
            self.db.rollback()
            return False

    def clear_expired_cache(self) -> int:
        """
        Remove all expired cache entries from the database.

        Returns:
            Number of cache entries that were deleted.
        """
        try:
            deleted = self.db.query(QueryCache).filter(
                QueryCache.expires_at < datetime.utcnow()
            ).delete()
            self.db.commit()
            logger.info(f"Cleared {deleted} expired cache entries")
            return deleted

        except Exception as e:
            logger.error(f"Error clearing expired cache: {str(e)}")
            self.db.rollback()
            return 0

    def clear_all_cache(self) -> int:
        """
        Remove all cache entries from the database.

        Returns:
            Number of cache entries that were deleted.
        """
        try:
            deleted = self.db.query(QueryCache).delete()
            self.db.commit()
            logger.info(f"Cleared all {deleted} cache entries")
            return deleted

        except Exception as e:
            logger.error(f"Error clearing all cache: {str(e)}")
            self.db.rollback()
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Retrieve cache performance and usage statistics.

        Computes counts of active and expired entries and identifies
        the most frequently accessed cached queries.

        Returns:
            Dictionary containing:
                - total_entries: Total number of cache entries
                - active_entries: Number of non-expired cache entries
                - expired_entries: Number of expired cache entries
                - top_queries: List of top 5 most accessed queries with hit counts
        """
        try:
            total_entries = self.db.query(QueryCache).count()
            expired_entries = self.db.query(QueryCache).filter(
                QueryCache.expires_at < datetime.utcnow()
            ).count()
            active_entries = total_entries - expired_entries

            top_queries = self.db.query(QueryCache).order_by(
                QueryCache.hit_count.desc()
            ).limit(5).all()

            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "expired_entries": expired_entries,
                "top_queries": [
                    {
                        "query": q.query_text,
                        "hits": q.hit_count,
                        "last_accessed": q.last_accessed.isoformat() if q.last_accessed else None
                    }
                    for q in top_queries
                ]
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}
