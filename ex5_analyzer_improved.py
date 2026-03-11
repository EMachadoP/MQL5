"""
EX5Analyzer Melhorado - Análise Forense de Arquivos EX5 (MetaTrader 5)
=======================================================================
Versão otimizada com tratamento de erros, performance melhorada e 
bibliotecas especializadas.

Autor: Análise Forense Python
Versão: 2.0
"""

import struct
import re
import json
import mmap
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Generator, Union, Tuple
from dataclasses import dataclass, asdict
from functools import lru_cache
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTES E PADRÕES PRECOMPILADOS
# ============================================================================

# Padrões regex precompilados para performance
STRING_PATTERN = re.compile(rb'[\x20-\x7E]{4,256}')  # ASCII printable
UTF8_STRING_PATTERN = re.compile(
    rb'(?:[\x20-\x7E]|\xC0-\xDF][\x80-\xBF]|\xE0-\xEF][\x80-\xBF]{2}'
    rb'|\xF0-\xF7][\x80-\xBF]{3}){4,256}'
)

# Magic numbers típicos de EX5 (assinaturas, headers)
EX5_SIGNATURES = {
    b'\x4D\x51\x4C\x35': 'MQL5 Header',  # 'MQL5' em ASCII
    b'\x45\x58\x35': 'EX5 Signature',      # 'EX5' em ASCII
}

# Constantes de análise
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1MB para chunking
MAX_STRING_LENGTH = 256
MIN_STRING_LENGTH = 4


# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================

@dataclass
class EX5Metadata:
    """Metadados extraídos de um arquivo EX5"""
    filepath: str
    file_size: int
    md5_hash: str
    sha256_hash: str
    strings_found: List[str]
    magic_numbers: List[int]
    constants: Dict[str, List[int]]
    possible_symbols: List[str]
    analysis_timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


@dataclass
class AnalysisConfig:
    """Configuração para análise de arquivos EX5"""
    min_string_length: int = 4
    max_string_length: int = 256
    magic_number_range: Tuple[int, int] = (100000, 999999)
    ma_period_range: Tuple[int, int] = (5, 1000)
    use_mmap: bool = True
    chunk_size: int = DEFAULT_CHUNK_SIZE
    encoding: str = 'utf-8'


# ============================================================================
# CLASSE PRINCIPAL MELHORADA
# ============================================================================

class EX5Analyzer:
    """
    Analisador forense para arquivos EX5 (Expert Advisors MetaTrader 5)
    
    Melhorias:
    - Suporte a arquivos grandes via mmap
    - Tratamento completo de erros
    - Regex precompilados
    - Alinhamento correto de memória
    - Generators para economia de memória
    """
    
    def __init__(self, filepath: Union[str, Path], config: Optional[AnalysisConfig] = None):
        """
        Inicializa o analisador EX5
        
        Args:
            filepath: Caminho para o arquivo EX5
            config: Configuração opcional de análise
        
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se o arquivo for muito pequeno ou inválido
            PermissionError: Se não houver permissão de leitura
        """
        self.config = config or AnalysisConfig()
        self.filepath = Path(filepath)
        
        # Validações iniciais
        self._validate_file()
        
        # Atributos lazy-loaded
        self._data: Optional[bytes] = None
        self._mm: Optional[mmap.mmap] = None
        self._metadata: Optional[EX5Metadata] = None
        
    def _validate_file(self) -> None:
        """Valida o arquivo antes de processar"""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.filepath}")
        
        if not self.filepath.is_file():
            raise ValueError(f"Caminho não é um arquivo: {self.filepath}")
        
        if not os.access(self.filepath, os.R_OK):
            raise PermissionError(f"Sem permissão de leitura: {self.filepath}")
        
        file_size = self.filepath.stat().st_size
        if file_size < 16:  # Tamanho mínimo para um EX5 válido
            raise ValueError(f"Arquivo muito pequeno ({file_size} bytes): {self.filepath}")
        
        logger.info(f"Arquivo validado: {self.filepath} ({file_size} bytes)")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - garante liberação de recursos"""
        self.close()
        return False
    
    def close(self) -> None:
        """Fecha recursos abertos"""
        if self._mm is not None:
            self._mm.close()
            self._mm = None
            logger.debug("mmap fechado")
    
    @property
    def data(self) -> bytes:
        """Acessa dados do arquivo (lazy loading com mmap)"""
        if self._data is None:
            if self.config.use_mmap and self.filepath.stat().st_size > self.config.chunk_size:
                # Usar mmap para arquivos grandes
                with open(self.filepath, 'rb') as f:
                    self._mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                    self._data = self._mm
            else:
                # Ler diretamente para arquivos pequenos
                with open(self.filepath, 'rb') as f:
                    self._data = f.read()
        return self._data
    
    def _compute_hashes(self) -> Tuple[str, str]:
        """Calcula MD5 e SHA256 do arquivo"""
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        
        with open(self.filepath, 'rb') as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
        
        return md5_hash.hexdigest(), sha256_hash.hexdigest()
    
    # ========================================================================
    # MÉTODOS DE EXTRAÇÃO DE STRINGS (OTIMIZADOS)
    # ========================================================================
    
    def extract_strings(self, min_length: Optional[int] = None, 
                       max_length: Optional[int] = None,
                       encoding: Optional[str] = None) -> List[str]:
        """
        Extrai strings legíveis do arquivo EX5
        
        Args:
            min_length: Comprimento mínimo da string (default: config.min_string_length)
            max_length: Comprimento máximo da string (default: config.max_string_length)
            encoding: Codificação para decodificação (default: config.encoding)
        
        Returns:
            Lista de strings encontradas
        """
        min_len = min_length or self.config.min_string_length
        max_len = max_length or self.config.max_string_length
        enc = encoding or self.config.encoding
        
        # Usar padrão precompilado se os parâmetros forem os padrões
        if min_len == MIN_STRING_LENGTH and max_len == MAX_STRING_LENGTH:
            pattern = STRING_PATTERN
        else:
            # Criar padrão dinâmico apenas quando necessário
            pattern = re.compile(rb'[\x20-\x7E]{' + str(min_len).encode() + b',' + 
                                str(max_len).encode() + b'}')
        
        try:
            matches = pattern.findall(self.data)
            strings = []
            for match in matches:
                try:
                    decoded = match.decode(enc, errors='ignore')
                    if decoded.strip():  # Ignorar strings vazias
                        strings.append(decoded)
                except UnicodeDecodeError:
                    continue
            return strings
        except Exception as e:
            logger.error(f"Erro ao extrair strings: {e}")
            return []
    
    def extract_strings_generator(self, min_length: Optional[int] = None) -> Generator[str, None, None]:
        """
        Versão generator de extract_strings - economia de memória
        
        Yields:
            Strings encontradas uma a uma
        """
        min_len = min_length or self.config.min_string_length
        pattern = re.compile(rb'[\x20-\x7E]{' + str(min_len).encode() + b',}')
        
        for match in pattern.finditer(self.data):
            try:
                decoded = match.group().decode('utf-8', errors='ignore')
                if decoded.strip():
                    yield decoded
            except UnicodeDecodeError:
                continue
    
    # ========================================================================
    # MÉTODOS DE ANÁLISE NUMÉRICA (CORRIGIDOS E OTIMIZADOS)
    # ========================================================================
    
    def find_constants(self) -> Dict[str, List[int]]:
        """
        Encontra constantes numéricas comuns em arquivos EX5
        
        Returns:
            Dicionário com categorias de constantes encontradas
        """
        patterns = {
            'ma_periods': set(),
            'rsi_levels': set(),
            'pips_values': set(),
            'volume_values': set(),
            'price_levels': set()
        }
        
        data = self.data
        min_period, max_period = self.config.ma_period_range
        
        # CORREÇÃO: Usar step=8 para alinhamento correto de double (64-bit)
        try:
            for i in range(0, len(data) - 8, 8):
                try:
                    # CORREÇÃO: Usar unpack_from para evitar slicing
                    val = struct.unpack_from('<d', data, i)[0]
                    
                    # Verificar se é um valor inteiro válido
                    if not (min_period < val < max_period):
                        continue
                    
                    int_val = int(val)
                    if val != int_val:
                        continue
                    
                    # Categorizar o valor
                    if int_val in [10, 12, 14, 20, 21, 50, 100, 200]:
                        patterns['ma_periods'].add(int_val)
                    elif int_val in [30, 70, 80, 20]:
                        patterns['rsi_levels'].add(int_val)
                    elif 1 <= int_val <= 500:
                        patterns['pips_values'].add(int_val)
                    elif 1000 <= int_val <= 100000:
                        patterns['volume_values'].add(int_val)
                        
                except struct.error:
                    # Ignorar erros de unpacking em dados malformados
                    continue
                    
        except Exception as e:
            logger.error(f"Erro ao encontrar constantes: {e}")
        
        # Converter sets para listas ordenadas
        return {k: sorted(list(v)) for k, v in patterns.items()}
    
    def find_magic_numbers(self) -> List[int]:
        """
        Busca Magic Numbers comuns (IDs de trades) em arquivos EX5
        
        Returns:
            Lista de magic numbers únicos encontrados
        """
        min_magic, max_magic = self.config.magic_number_range
        candidates: Set[int] = set()
        data = self.data
        
        try:
            # OTIMIZAÇÃO: Usar set durante iteração para deduplicação imediata
            for i in range(0, len(data) - 4, 4):
                try:
                    val = struct.unpack_from('<I', data, i)[0]
                    if min_magic < val < max_magic:
                        candidates.add(val)
                except struct.error:
                    continue
        except Exception as e:
            logger.error(f"Erro ao encontrar magic numbers: {e}")
        
        return sorted(list(candidates))
    
    def find_all_integers(self, bit_size: int = 32, 
                         signed: bool = True) -> Generator[int, None, None]:
        """
        Generator para encontrar todos os inteiros no arquivo
        
        Args:
            bit_size: Tamanho do inteiro (16, 32, 64)
            signed: Se True, interpreta como signed int
        
        Yields:
            Inteiros encontrados
        """
        format_map = {
            (16, True): '<h', (16, False): '<H',
            (32, True): '<i', (32, False): '<I',
            (64, True): '<q', (64, False): '<Q'
        }
        
        fmt = format_map.get((bit_size, signed))
        if not fmt:
            raise ValueError(f"Tamanho de bit não suportado: {bit_size}")
        
        size = bit_size // 8
        data = self.data
        
        for i in range(0, len(data) - size, size):
            try:
                yield struct.unpack_from(fmt, data, i)[0]
            except struct.error:
                continue
    
    # ========================================================================
    # MÉTODOS DE ANÁLISE ESPECÍFICA EX5
    # ========================================================================
    
    def find_possible_symbols(self) -> List[str]:
        """
        Identifica possíveis símbolos de trading (EURUSD, GBPJPY, etc.)
        
        Returns:
            Lista de símbolos potenciais
        """
        # Padrão para símbolos de forex (6 caracteres maiúsculos)
        symbol_pattern = re.compile(rb'[A-Z]{6}')
        
        symbols = set()
        for match in symbol_pattern.finditer(self.data):
            try:
                symbol = match.group().decode('ascii')
                # Validar se parece um par de moedas
                if self._is_valid_symbol(symbol):
                    symbols.add(symbol)
            except:
                continue
        
        return sorted(list(symbols))
    
    def _is_valid_symbol(self, symbol: str) -> bool:
        """Valida se uma string parece ser um símbolo de trading válido"""
        major_currencies = {'EUR', 'USD', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD'}
        if len(symbol) != 6:
            return False
        base = symbol[:3]
        quote = symbol[3:]
        return base in major_currencies and quote in major_currencies
    
    def detect_ex5_header(self) -> Optional[Dict]:
        """
        Detecta e analisa o header do arquivo EX5
        
        Returns:
            Dicionário com informações do header ou None
        """
        data = self.data
        header_info = {}
        
        # Verificar assinaturas conhecidas
        for sig, name in EX5_SIGNATURES.items():
            if sig in data[:256]:  # Procurar no início do arquivo
                header_info['signature'] = name
                header_info['signature_offset'] = data.find(sig)
                break
        
        # Tentar extrair versão (se presente)
        version_pattern = re.compile(rb'[\x00-\xFF]{4}(\d+\.\d+)')
        match = version_pattern.search(data[:512])
        if match:
            header_info['version'] = match.group(1).decode('ascii', errors='ignore')
        
        return header_info if header_info else None
    
    # ========================================================================
    # MÉTODOS DE ANÁLISE COMPLETA
    # ========================================================================
    
    def analyze(self) -> EX5Metadata:
        """
        Realiza análise completa do arquivo EX5
        
        Returns:
            EX5Metadata com todos os metadados extraídos
        """
        logger.info(f"Iniciando análise de {self.filepath}")
        
        # Calcular hashes
        md5, sha256 = self._compute_hashes()
        
        # Extrair informações
        strings = self.extract_strings()
        magic_numbers = self.find_magic_numbers()
        constants = self.find_constants()
        symbols = self.find_possible_symbols()
        
        self._metadata = EX5Metadata(
            filepath=str(self.filepath),
            file_size=self.filepath.stat().st_size,
            md5_hash=md5,
            sha256_hash=sha256,
            strings_found=strings[:1000],  # Limitar para não sobrecarregar
            magic_numbers=magic_numbers[:100],
            constants=constants,
            possible_symbols=symbols,
            analysis_timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Análise concluída: {len(strings)} strings, {len(magic_numbers)} magic numbers")
        
        return self._metadata
    
    def get_report(self, format: str = 'json') -> str:
        """
        Gera relatório da análise
        
        Args:
            format: 'json', 'dict', ou 'txt'
        
        Returns:
            Relatório no formato especificado
        """
        if self._metadata is None:
            self.analyze()
        
        if format == 'json':
            return self._metadata.to_json()
        elif format == 'dict':
            return str(self._metadata.to_dict())
        elif format == 'txt':
            return self._generate_text_report()
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _generate_text_report(self) -> str:
        """Gera relatório em formato texto legível"""
        m = self._metadata
        report = f"""
================================================================================
RELATÓRIO DE ANÁLISE EX5
================================================================================
Arquivo: {m.filepath}
Tamanho: {m.file_size:,} bytes
MD5: {m.md5_hash}
SHA256: {m.sha256_hash}
Timestamp: {m.analysis_timestamp}

--- STRINGS ENCONTRADAS ({len(m.strings_found)}) ---
"""
        for i, s in enumerate(m.strings_found[:50], 1):
            report += f"  {i:3d}. {s[:80]}\n"
        
        report += f"\n--- MAGIC NUMBERS ({len(m.magic_numbers)}) ---\n"
        for i, mn in enumerate(m.magic_numbers[:20], 1):
            report += f"  {i:3d}. {mn}\n"
        
        report += f"\n--- CONSTANTES ---\n"
        for category, values in m.constants.items():
            if values:
                report += f"  {category}: {values[:10]}\n"
        
        report += f"\n--- SÍMBOLOS POSSÍVEIS ({len(m.possible_symbols)}) ---\n"
        for sym in m.possible_symbols:
            report += f"  - {sym}\n"
        
        report += "\n================================================================================\n"
        return report


# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

def batch_analyze(directory: Union[str, Path], 
                  pattern: str = "*.ex5",
                  config: Optional[AnalysisConfig] = None) -> List[EX5Metadata]:
    """
    Analisa múltiplos arquivos EX5 em um diretório
    
    Args:
        directory: Diretório contendo arquivos EX5
        pattern: Padrão de glob para matching
        config: Configuração de análise
    
    Returns:
        Lista de metadados de cada arquivo
    """
    directory = Path(directory)
    results = []
    
    for filepath in directory.glob(pattern):
        try:
            with EX5Analyzer(filepath, config) as analyzer:
                metadata = analyzer.analyze()
                results.append(metadata)
        except Exception as e:
            logger.error(f"Erro ao analisar {filepath}: {e}")
    
    return results


def compare_ex5_files(filepath1: Union[str, Path], 
                      filepath2: Union[str, Path]) -> Dict:
    """
    Compara dois arquivos EX5 e retorna diferenças
    
    Args:
        filepath1: Primeiro arquivo
        filepath2: Segundo arquivo
    
    Returns:
        Dicionário com diferenças encontradas
    """
    with EX5Analyzer(filepath1) as a1, EX5Analyzer(filepath2) as a2:
        m1 = a1.analyze()
        m2 = a2.analyze()
    
    differences = {
        'same_size': m1.file_size == m2.file_size,
        'same_md5': m1.md5_hash == m2.md256_hash,
        'same_sha256': m1.sha256_hash == m2.sha256_hash,
        'common_strings': list(set(m1.strings_found) & set(m2.strings_found)),
        'unique_strings_1': list(set(m1.strings_found) - set(m2.strings_found)),
        'unique_strings_2': list(set(m2.strings_found) - set(m1.strings_found)),
    }
    
    return differences


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Exemplo de uso básico
    try:
        # Configuração personalizada
        config = AnalysisConfig(
            min_string_length=5,
            use_mmap=True,
            magic_number_range=(10000, 9999999)
        )
        
        # Análise de arquivo
        with EX5Analyzer("exemplo.ex5", config) as analyzer:
            # Análise completa
            metadata = analyzer.analyze()
            print(metadata.to_json())
            
            # Ou relatório em texto
            # print(analyzer.get_report('txt'))
            
    except FileNotFoundError:
        print("Arquivo não encontrado. Crie um arquivo exemplo.ex5 para testar.")
    except Exception as e:
        print(f"Erro: {e}")
