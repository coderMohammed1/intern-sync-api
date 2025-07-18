import base64
import io
import os
import tempfile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import jwt
from ..models import Applications

# PDF parsing imports - we'll use multiple libraries for better reliability
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

class PDFTextExtract(APIView):
    """
    Extract text content from PDF files using multiple parsing libraries
    """
    
    def post(self, request, format=None):
        """
        Extract text from a PDF file
        Expected payload: {
            "pdf_base64": "base64_encoded_pdf_content",
            "application_id": "optional_application_id"
        }
        """
        # Debug: Log incoming request
        print(f"POST request received - Content Type: {request.content_type}")
        print(f"Request data keys: {list(request.data.keys()) if hasattr(request, 'data') else 'No data attr'}")
        print(f"Request data type: {type(request.data)}")
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("Auth header missing or invalid")
            return Response({'error': 'Authorization header missing or invalid'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            print(f"JWT payload decoded successfully: {payload}")
            
            # Get PDF data from request
            pdf_base64 = request.data.get('pdf_base64')
            application_id = request.data.get('application_id')
            
            print(f"PDF base64 length: {len(pdf_base64) if pdf_base64 else 0}")
            print(f"Application ID: {application_id}")
            
            if not pdf_base64:
                print("pdf_base64 field is missing from request")
                return Response({'error': 'pdf_base64 is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Extract text using available libraries
            extracted_text = self.extract_text_from_base64(pdf_base64)
            
            if not extracted_text:
                print("Failed to extract text from PDF")
                return Response({'error': 'Could not extract text from PDF'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            print(f"Successfully extracted text, length: {len(extracted_text)}")
            return Response({
                'success': True,
                'text': extracted_text,
                'text_length': len(extracted_text),
                'extraction_method': self.get_available_methods()
            }, status=status.HTTP_200_OK)
            
        except jwt.ExpiredSignatureError:
            print("JWT token has expired")
            return Response({'error': 'Token has expired'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            print("JWT token is invalid")
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return Response({'error': f'Error extracting PDF text: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request, application_id, format=None):
        """
        Extract text from an existing application's CV file
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authorization header missing or invalid'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            
            if payload["role"] == "c":
                # Get the application and CV file
                application = Applications.objects.filter(
                    id=application_id, 
                    cid=payload['cid']
                ).first()
                
                if not application:
                    return Response({'error': 'Application not found'}, 
                                  status=status.HTTP_404_NOT_FOUND)
                
                # Read the CV file
                cv_path = application.path
                if not os.path.exists(cv_path):
                    return Response({'error': 'CV file not found'}, 
                                  status=status.HTTP_404_NOT_FOUND)
                
                # Extract text from the file
                extracted_text = self.extract_text_from_file(cv_path)
                
                if not extracted_text:
                    return Response({'error': 'Could not extract text from CV'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                
                return Response({
                    'success': True,
                    'text': extracted_text,
                    'text_length': len(extracted_text),
                    'file_path': cv_path,
                    'extraction_method': self.get_available_methods()
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({'error': 'Unauthorized access'}, 
                              status=status.HTTP_403_FORBIDDEN)
                
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': f'Error extracting PDF text: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def extract_text_from_base64(self, pdf_base64):
        """Extract text from base64 encoded PDF"""
        try:
            print(f"Attempting to decode base64 PDF, length: {len(pdf_base64)}")
            # Decode base64
            pdf_data = base64.b64decode(pdf_base64)
            print(f"Decoded PDF data size: {len(pdf_data)} bytes")
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_data)
                temp_file_path = temp_file.name
            
            print(f"Created temporary file: {temp_file_path}")
            
            try:
                # Extract text from temporary file
                text = self.extract_text_from_file(temp_file_path)
                return text
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    print("Cleaned up temporary file")
                    
        except Exception as e:
            print(f"Error in extract_text_from_base64: {e}")
            return None
    
    def extract_text_from_file(self, file_path):
        """Extract text from PDF file using multiple methods"""
        text = ""
        
        print(f"Attempting to extract text from: {file_path}")
        print(f"Available extraction methods: {self.get_available_methods()}")
        
        # Method 1: Try PyMuPDF (fitz) - most reliable
        if PYMUPDF_AVAILABLE:
            try:
                print("Trying PyMuPDF extraction...")
                text = self.extract_with_pymupdf(file_path)
                if text and len(text.strip()) > 50:  # Good extraction
                    print(f"PyMuPDF extraction successful, text length: {len(text)}")
                    return text
            except Exception as e:
                print(f"PyMuPDF extraction failed: {e}")
        
        # Method 2: Try pdfplumber - good for tables and layout
        if PDFPLUMBER_AVAILABLE:
            try:
                print("Trying pdfplumber extraction...")
                text = self.extract_with_pdfplumber(file_path)
                if text and len(text.strip()) > 50:  # Good extraction
                    print(f"pdfplumber extraction successful, text length: {len(text)}")
                    return text
            except Exception as e:
                print(f"pdfplumber extraction failed: {e}")
        
        # Method 3: Try PyPDF2 - fallback
        if PYPDF2_AVAILABLE:
            try:
                print("Trying PyPDF2 extraction...")
                text = self.extract_with_pypdf2(file_path)
                if text and len(text.strip()) > 50:  # Good extraction
                    print(f"PyPDF2 extraction successful, text length: {len(text)}")
                    return text
            except Exception as e:
                print(f"PyPDF2 extraction failed: {e}")
        
        print(f"All extraction methods completed. Final text length: {len(text) if text else 0}")
        return text if text else None
    
    def extract_with_pymupdf(self, file_path):
        """Extract text using PyMuPDF (fitz)"""
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    def extract_with_pdfplumber(self, file_path):
        """Extract text using pdfplumber"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    
    def extract_with_pypdf2(self, file_path):
        """Extract text using PyPDF2"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def get_available_methods(self):
        """Return list of available extraction methods"""
        methods = []
        if PYMUPDF_AVAILABLE:
            methods.append("PyMuPDF")
        if PDFPLUMBER_AVAILABLE:
            methods.append("pdfplumber")
        if PYPDF2_AVAILABLE:
            methods.append("PyPDF2")
        return methods
