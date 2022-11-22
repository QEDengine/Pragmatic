#pragma once

// Standard library
#include <vector>	// vector
#include <string>	// string
// Clang
#include <clang/Lex/Pragma.h>			// PragmaHandler
#include <clang/Lex/Preprocessor.h>		// PragmaHandlerRegistry
#include <clang/Lex/PreprocessorOptions.h>
// Pragmatic
#include "PragmaHandler.hpp"
#include "Utility.hpp"

#define PREAMBLE_PRAGMA_TOKEN "preamble"
#define INCLUDE_TOKEN "include"

namespace QED { namespace Pragmatic
{
	class Callbacks : public clang::PPCallbacks
	{
		protected:
		clang::Preprocessor& preprocessor;
		clang::SourceManager& sourceManager;

		public:
		Callbacks(clang::Preprocessor& preprocessor) : preprocessor(preprocessor), sourceManager(preprocessor.getSourceManager()) { }
	};

	class EndOfMainFileCallback : public Callbacks
	{
		public:
		EndOfMainFileCallback(clang::Preprocessor& pp) : Callbacks(pp) { }

		virtual void EndOfMainFile() override
		{
			Meta::GetInstance(preprocessor).Write();
		}
	};

	class IncludeCallback : public Callbacks
	{
		public:
		IncludeCallback(clang::Preprocessor& pp) : Callbacks(pp) { }

		virtual void InclusionDirective
		(
			clang::SourceLocation HashLoc,
			const clang::Token &IncludeTok,
			clang::StringRef FileName,
			bool IsAngled,
			clang::CharSourceRange FilenameRange,
			clang::Optional<clang::FileEntryRef> File,
			clang::StringRef SearchPath,
			clang::StringRef RelativePath,
			const clang::Module *Imported,
			clang::SrcMgr::CharacteristicKind FileType
		) override
		{
			if (Imported == nullptr && FileType == clang::SrcMgr::CharacteristicKind::C_User)
			{
				std::string path = NormalizePath(sourceManager.getFilename(HashLoc).str(), sourceManager.getFileManager().getFileSystemOpts().WorkingDir);

				auto& meta = Meta::GetInstance(preprocessor);
				meta.json["graph"]["nodes"][RelativePath.str()]["metadata"]["defined"] = path;
				meta.json["graph"]["edges"].push_back
				({
					{"source", RelativePath.str()},
					{"target", path},
					{"relation", INCLUDE_TOKEN},
					{"metadata", {{"defined", path}}}
				});
			}
		}
	};

	class PreamblePragmaHandler : public PragmaHandler
	{
		public: // Constructor
		PreamblePragmaHandler() : PragmaHandler(PREAMBLE_PRAGMA_TOKEN, {{}}) { }

		public: // Clang functions
		virtual bool CheckTokens(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics, clang::SourceLocation sourceLocation) override { return true; }
		virtual std::string Response(clang::Preprocessor &preprocessor, std::vector<std::string> tokens, clang::DiagnosticsEngine& diagnostics) override
		{
			auto mainFileID = preprocessor.getSourceManager().getFileEntryForID(preprocessor.getSourceManager().getMainFileID())->getName().str();

			auto& meta = Meta::GetInstance(preprocessor);
			meta.ClearDefinitionsForFile(mainFileID);

			preprocessor.addPPCallbacks(std::make_unique<EndOfMainFileCallback>(preprocessor));
			preprocessor.addPPCallbacks(std::make_unique<IncludeCallback>(preprocessor));
			return "";
		}
	};
}} // namespace QED::Pragmatic
