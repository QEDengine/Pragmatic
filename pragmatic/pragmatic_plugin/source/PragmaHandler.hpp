#pragma once
// Standard library
#include <vector>
#include <string>
// LLVM
#include "clang/Basic/Diagnostic.h"
#include "clang/Basic/SourceLocation.h"
#include "clang/Basic/TokenKinds.h"
#include "clang/Lex/Token.h"
#include "llvm/ADT/StringRef.h"
// Clang
#include "clang/Lex/Pragma.h"
// External
#include <nlohmann/json.hpp>
using json = nlohmann::ordered_json;
// Pragmatic
#include "Meta.hpp"

namespace QED { namespace Pragmatic
{
	struct PragmaToken
	{
		bool isStringLiteral = false;
	};

	class PragmaHandler : public clang::PragmaHandler
	{
		public: // Constructor / destructor
		PragmaHandler(llvm::StringRef name, std::vector<PragmaToken> format, uint8_t optional = 1) : clang::PragmaHandler(name), format(format), optional(optional) { }

		protected:
		std::vector<PragmaToken> format;
		uint8_t optional;
		std::string sourceFilePath;
		std::string sourceFileDir;
		std::string includePath;

		public: // Clang hooks
		virtual void HandlePragma(clang::Preprocessor &preprocessor, clang::PragmaIntroducer introducer, clang::Token &sourceToken) final;
		
		protected: // Inherited customization methods
		virtual bool CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation) = 0;
		virtual std::string Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics) = 0;
	};
}} // namesapce QED::Pragmatic