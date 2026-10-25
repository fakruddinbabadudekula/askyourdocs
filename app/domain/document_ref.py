from dataclasses import dataclass
from uuid import UUID

@dataclass
class DocumentRef:
    doc_id:UUID
    file_id:UUID
    
    